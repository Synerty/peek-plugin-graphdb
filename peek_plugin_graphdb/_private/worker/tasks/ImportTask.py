import json
import logging
from collections import defaultdict
from copy import copy
from datetime import datetime
from typing import List, Dict, Set, Tuple

import pytz
from sqlalchemy import select, bindparam, and_
from txcelery.defer import DeferrableTask
from vortex.Payload import Payload

from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_graphdb._private.storage.GraphDbCompilerQueue import GraphDbCompilerQueue
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from peek_plugin_graphdb._private.storage.GraphDbSegment import GraphDbSegment
from peek_plugin_graphdb._private.worker.CeleryApp import celeryApp
from peek_plugin_graphdb._private.worker.tasks._CalcChunkKey import makeChunkKey
from peek_plugin_graphdb.tuples.GraphDbImportSegmentTuple import GraphDbImportSegmentTuple

logger = logging.getLogger(__name__)


# We need to insert the into the following tables:
# GraphDbSegment - or update it's details if required
# GraphDbIndex - The index of the keywords for the object
# GraphDbSegmentRoute - delete old importGroupHash
# GraphDbSegmentRoute - insert the new routes


@DeferrableTask
@celeryApp.task(bind=True)
def deleteSegment(self, modelSetKey: str, segmentKey: str) -> None:
    pass


@DeferrableTask
@celeryApp.task(bind=True)
def createOrUpdateSegments(self, segmentEncodedPayload: bytes) -> None:
    # Decode arguments
    newSegments: List[GraphDbImportSegmentTuple] = (
        Payload().fromEncodedPayload(segmentEncodedPayload).tuples
    )

    _validateNewSegments(newSegments)

    modelSetIdByKey = _loadModelSets()

    # Do the import
    try:

        segmentByModelKey = defaultdict(list)
        for segment in newSegments:
            segmentByModelKey[segment.modelSetKey].append(segment)

        for modelSetKey, segments in segmentByModelKey.items():
            modelSetId = modelSetIdByKey.get(modelSetKey)
            if modelSetId is None:
                modelSetId = _makeModelSet(modelSetKey)
                modelSetIdByKey[modelSetKey] = modelSetId

            _insertOrUpdateObjects(segments, modelSetId)

    except Exception as e:
        logger.debug("Retrying import graphDb objects, %s", e)
        raise self.retry(exc=e, countdown=3)



def _validateNewSegments(newSegments: List[GraphDbImportSegmentTuple]) -> None:
    for segment in newSegments:
        if not segment.key:
            raise Exception("key is empty for %s" % segment)

        if not segment.modelSetKey:
            raise Exception("modelSetKey is empty for %s" % segment)


def _loadModelSets() -> Dict[str, int]:
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


def _makeModelSet(modelSetKey: str) -> int:
    # Get the model set
    dbSession = CeleryDbConn.getDbSession()
    try:
        newItem = GraphDbModelSet(key=modelSetKey, name=modelSetKey)
        dbSession.add(newItem)
        dbSession.commit()
        return newItem.id

    finally:
        dbSession.close()



def _insertOrUpdateObjects(newSegments: List[GraphDbImportSegmentTuple],
                           modelSetId: int) -> None:
    """ Insert or Update Objects

    1) Find objects and update them
    2) Insert object if the are missing

    """

    segmentTable = GraphDbSegment.__table__
    queueTable = GraphDbCompilerQueue.__table__

    startTime = datetime.now(pytz.utc)

    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()

    try:
        importHashSet = set()
        dontDeleteObjectIds=[]
        objectIdByKey: Dict[str, int] = {}

        objectKeys = [o.key for o in newSegments]
        chunkKeysForQueue: Set[Tuple[str, str]] = set()

        # Query existing objects
        results = list(conn.execute(select(
            columns=[segmentTable.c.id, segmentTable.c.key,
                     segmentTable.c.chunkKey, segmentTable.c.segmentJson],
            whereclause=and_(segmentTable.c.key.in_(objectKeys),
                             segmentTable.c.modelSetId == modelSetId)
        )))

        foundObjectByKey = {o.key: o for o in results}
        del results

        # Get the IDs that we need
        newIdGen = CeleryDbConn.prefetchDeclarativeIds(
            GraphDbSegment, len(newSegments) - len(foundObjectByKey)
        )

        # Create state arrays
        inserts = []
        updates = []

        # Work out which objects have been updated or need inserting
        for importSegment in newSegments:
            importHashSet.add(importSegment.importGroupHash)

            existingObject = foundObjectByKey.get(importSegment.key)

            packedJsonDict = copy(importSegment.segment)
            packedJsonDict['_msid'] = modelSetId
            segmentJson = json.dumps(packedJsonDict, sort_keys=True)

            # Work out if we need to update the object type
            if existingObject:
                updates.append(
                    dict(b_id=existingObject.id,
                         b_segmentJson=segmentJson)
                )
                dontDeleteObjectIds.append(existingObject.id)

            else:
                id_ = next(newIdGen)
                existingObject = GraphDbSegment(
                    id=id_,
                    modelSetId=modelSetId,
                    key=importSegment.key,
                    importGroupHash=importSegment.importGroupHash,
                    chunkKey=makeChunkKey(importSegment.modelSetKey, importSegment.key),
                    segmentJson=segmentJson
                )
                inserts.append(existingObject.tupleToSqlaBulkInsertDict())

            objectIdByKey[existingObject.key] = existingObject.id
            chunkKeysForQueue.add((modelSetId, existingObject.chunkKey))

        if importHashSet:
            conn.execute(
                segmentTable
                    .delete(and_(~segmentTable.c.id.in_(dontDeleteObjectIds),
                                 segmentTable.c.importGroupHash.in_(importHashSet)))
            )

        # Insert the GraphDb Objects
        if inserts:
            conn.execute(segmentTable.insert(), inserts)

        if updates:
            stmt = (
                segmentTable.update()
                    .where(segmentTable.c.id == bindparam('b_id'))
                    .values(segmentTypeId=bindparam('b_typeId'),
                            segmentJson=bindparam('b_segmentJson'))
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
