import logging
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Set, Tuple

import pytz
from peek_plugin_base.worker import CeleryDbConn
from sqlalchemy import select, bindparam, and_
from txcelery.defer import DeferrableTask
from vortex.Payload import Payload

from peek_plugin_graphdb._private.storage.GraphDbModelSet import \
    GraphDbModelSet
from peek_plugin_graphdb._private.storage.ItemKeyIndex import \
    ItemKeyIndex
from peek_plugin_graphdb._private.storage.ItemKeyIndexCompilerQueue import \
    ItemKeyIndexCompilerQueue
from peek_plugin_graphdb._private.storage.ItemKeyType import \
    ItemKeyType
from peek_plugin_graphdb._private.worker.CeleryApp import celeryApp
from peek_plugin_graphdb._private.worker.tasks._ItemKeyIndexCalcChunkKey import \
    makeChunkKey
from ServerStatusTuple.tuples.ItemKeyImportTuple import ItemKeyImportTuple

logger = logging.getLogger(__name__)


@DeferrableTask
@celeryApp.task(bind=True)
def createOrUpdateItemKeys(self, itemKeysEncodedPayload: bytes) -> None:
    # Decode arguments
    newItemKeys: List[ItemKeyImportTuple] = (
        Payload().fromEncodedPayload(itemKeysEncodedPayload).tuples
    )

    _validateNewItemKeyIndexs(newItemKeys)

    modelSetIdByKey = _loadGraphDbModelSets()

    # Do the import
    try:

        itemKeyIndexByModelKey = defaultdict(list)
        for itemKeyIndex in newItemKeys:
            itemKeyIndexByModelKey[itemKeyIndex.modelSetKey].append(itemKeyIndex)

        for modelSetKey, itemKeyIndexs in itemKeyIndexByModelKey.items():
            modelSetId = modelSetIdByKey.get(modelSetKey)
            if modelSetId is None:
                modelSetId = _makeGraphDbModelSet(modelSetKey)
                modelSetIdByKey[modelSetKey] = modelSetId

            itemKeyTypeIdsByName = _prepareLookups(itemKeyIndexs, modelSetId)
            _insertOrUpdateObjects(itemKeyIndexs, modelSetId, itemKeyTypeIdsByName)

    except Exception as e:
        logger.debug("Retrying import graphdbobjects, %s", e)
        raise self.retry(exc=e, countdown=3)


def _validateNewItemKeyIndexs(newItemKeys: List[ItemKeyImportTuple]) -> None:
    for itemKeyIndex in newItemKeys:
        if not itemKeyIndex.key:
            raise Exception("key is empty for %s" % itemKeyIndex)

        if not itemKeyIndex.modelSetKey:
            raise Exception("modelSetKey is empty for %s" % itemKeyIndex)

        if not itemKeyIndex.itemKeyTypeKey:
            raise Exception("itemKeyTypeKey is empty for %s" % itemKeyIndex)

        # if not itemKeyIndex.itemKeyIndex:
        #     raise Exception("itemKeyIndex is empty for %s" % itemKeyIndex)


def _loadGraphDbModelSets() -> Dict[str, int]:
    # Get the model set
    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    try:
        modelSetTable = GraphDbModelSet.__table__
        results = list(conn.execute(select(
            columns=[modelSetTable.c.id, modelSetTable.c.key]
        )))
        modelSetIdByKey = {o.key: o.id for o in results}
        del results

    finally:
        conn.close()
    return modelSetIdByKey


def _makeGraphDbModelSet(modelSetKey: str) -> int:
    # Get the model set
    dbSession = CeleryDbConn.getDbSession()
    try:
        newItem = GraphDbModelSet(key=modelSetKey, name=modelSetKey)
        dbSession.add(newItem)
        dbSession.commit()
        return newItem.id

    finally:
        dbSession.close()


def _prepareLookups(newItemKeys: List[ItemKeyImportTuple], modelSetId: int
                    ) -> Dict[str, int]:
    """ Check Or Insert ItemKeys

    """

    dbSession = CeleryDbConn.getDbSession()

    startTime = datetime.now(pytz.utc)

    try:

        itemKeyTypeKeys = set()

        for o in newItemKeys:
            o.itemKeyTypeKey = o.itemKeyTypeKey.lower()
            itemKeyTypeKeys.add(o.itemKeyTypeKey)

        # Prepare Object Types
        itemKeyTypes = (
            dbSession.query(ItemKeyType)
                .filter(ItemKeyType.modelSetId == modelSetId)
                .all()
        )
        itemKeyTypeKeys -= set([o.key for o in itemKeyTypes])

        if not itemKeyTypeKeys:
            itemKeyTypeIdsByKey = {o.key: o.id for o in itemKeyTypes}

        else:
            for newType in itemKeyTypeKeys:
                dbSession.add(ItemKeyType(
                    key=newType, name=newType, modelSetId=modelSetId
                ))

            dbSession.commit()

            itemKeyTypes = dbSession.query(ItemKeyType).all()
            itemKeyTypeIdsByKey = {o.key: o.id for o in itemKeyTypes}

        logger.debug("Prepared lookups in %s", (datetime.now(pytz.utc) - startTime))

        return itemKeyTypeIdsByKey

    except Exception as e:
        dbSession.rollback()
        raise

    finally:
        dbSession.close()


def _insertOrUpdateObjects(newItemKeys: List[ItemKeyImportTuple],
                           modelSetId: int,
                           itemKeyTypeIdsByName: Dict[str, int]) -> None:
    """ Insert or Update Objects

    1) Find objects and update them
    2) Insert object if the are missing

    """

    itemKeyIndexTable = ItemKeyIndex.__table__
    queueTable = ItemKeyIndexCompilerQueue.__table__

    startTime = datetime.now(pytz.utc)

    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()

    try:
        importHashSet = set()
        dontDeleteObjectIds = []
        objectIdByKey: Dict[str, int] = {}

        objectKeys = [o.key for o in newItemKeys]
        chunkKeysForQueue: Set[Tuple[str, str]] = set()

        # Query existing objects
        results = list(conn.execute(select(
            columns=[itemKeyIndexTable.c.id, itemKeyIndexTable.c.key,
                     itemKeyIndexTable.c.chunkKey, itemKeyIndexTable.c.packedJson],
            whereclause=and_(itemKeyIndexTable.c.key.in_(objectKeys),
                             itemKeyIndexTable.c.modelSetId == modelSetId)
        )))

        foundObjectByKey = {o.key: o for o in results}
        del results

        # Get the IDs that we need
        newIdGen = CeleryDbConn.prefetchDeclarativeIds(
            ItemKeyIndex, len(newItemKeys) - len(foundObjectByKey)
        )

        # Create state arrays
        inserts = []
        updates = []

        # Work out which objects have been updated or need inserting
        for importItemKeyIndex in newItemKeys:
            importHashSet.add(importItemKeyIndex.importGroupHash)

            existingObject = foundObjectByKey.get(importItemKeyIndex.key)
            importItemKeyTypeId = itemKeyTypeIdsByName[
                importItemKeyIndex.itemKeyTypeKey]

            packedJson = importItemKeyIndex.packJson(modelSetId, importItemKeyTypeId)

            # Work out if we need to update the object type
            if existingObject:
                updates.append(
                    dict(b_id=existingObject.id,
                         b_typeId=importItemKeyTypeId,
                         b_packedJson=packedJson)
                )
                dontDeleteObjectIds.append(existingObject.id)

            else:
                id_ = next(newIdGen)
                existingObject = ItemKeyIndex(
                    id=id_,
                    modelSetId=modelSetId,
                    itemKeyTypeId=importItemKeyTypeId,
                    key=importItemKeyIndex.key,
                    importGroupHash=importItemKeyIndex.importGroupHash,
                    chunkKey=makeChunkKey(importItemKeyIndex.modelSetKey,
                                          importItemKeyIndex.key),
                    packedJson=packedJson
                )
                inserts.append(existingObject.tupleToSqlaBulkInsertDict())

            objectIdByKey[existingObject.key] = existingObject.id
            chunkKeysForQueue.add((modelSetId, existingObject.chunkKey))

        if importHashSet:
            conn.execute(
                itemKeyIndexTable
                    .delete(and_(~itemKeyIndexTable.c.id.in_(dontDeleteObjectIds),
                                 itemKeyIndexTable.c.importGroupHash.in_(importHashSet)))
            )

        # Insert the ItemKeyIndex Objects
        if inserts:
            conn.execute(itemKeyIndexTable.insert(), inserts)

        if updates:
            stmt = (
                itemKeyIndexTable.update()
                    .where(itemKeyIndexTable.c.id == bindparam('b_id'))
                    .values(itemKeyTypeId=bindparam('b_typeId'),
                            packedJson=bindparam('b_packedJson'))
            )
            conn.execute(stmt, updates)

        if chunkKeysForQueue:
            conn.execute(
                queueTable.insert(),
                [dict(modelSetId=m, chunkKey=c) for m, c in chunkKeysForQueue]
            )

        if inserts or updates or chunkKeysForQueue:
            transaction.commit()
        else:
            transaction.rollback()

        logger.debug("Inserted %s updated %s queued %s chunks in %s",
                     len(inserts), len(updates), len(chunkKeysForQueue),
                     (datetime.now(pytz.utc) - startTime))

    except Exception:
        transaction.rollback()
        raise

    finally:
        conn.close()
