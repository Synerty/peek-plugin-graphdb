import logging
from collections import defaultdict
from datetime import datetime
from typing import List, Dict

import pytz
from sqlalchemy import select, and_
from txcelery.defer import DeferrableTask
from vortex.Payload import Payload

from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from peek_plugin_graphdb._private.storage.GraphDbTraceConfig import GraphDbTraceConfig
from peek_plugin_graphdb._private.storage.GraphDbTraceConfigRule import \
    GraphDbTraceConfigRule
from peek_plugin_graphdb._private.worker.CeleryApp import celeryApp
from peek_plugin_graphdb._private.worker.tasks._CalcChunkKey import makeChunkKey
from peek_plugin_graphdb.tuples.GraphDbImportTraceConfigTuple import \
    GraphDbImportTraceConfigTuple

logger = logging.getLogger(__name__)


@DeferrableTask
@celeryApp.task(bind=True)
def deleteTraceConfig(self, modelSetKey: str, traceConfigKeys: List[str]) -> None:
    startTime = datetime.now(pytz.utc)

    traceConfigTable = GraphDbTraceConfig.__table__

    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()
    try:
        chunkKeys = {
            makeChunkKey(modelSetKey, key) for key in traceConfigKeys
        }

        modelSetIdByKey = _loadModelSets()
        modelSetId = modelSetIdByKey[modelSetKey]

        conn.execute(
            traceConfigTable.delete(and_(traceConfigTable.c.key.in_(traceConfigKeys),
                                         traceConfigTable.c.modelSetId == modelSetId))
        )

        transaction.commit()

        logger.debug("Deleted %s, queued %s chunks in %s",
                     len(traceConfigKeys), len(chunkKeys),
                     (datetime.now(pytz.utc) - startTime))

    except Exception as e:
        transaction.rollback()
        logger.debug("Retrying import graphDb objects, %s", e)
        raise self.retry(exc=e, countdown=3)


    finally:
        conn.close()


@DeferrableTask
@celeryApp.task(bind=True)
def createOrUpdateTraceConfigs(self, traceConfigEncodedPayload: bytes
                               ) -> Dict[int, List[str]]:
    # Decode arguments
    newTraceConfigs: List[GraphDbImportTraceConfigTuple] = (
        Payload().fromEncodedPayload(traceConfigEncodedPayload).tuples
    )

    _validateNewTraceConfigs(newTraceConfigs)

    modelSetIdByKey = _loadModelSets()

    # Do the import
    try:
        insertedOrCreated: Dict[int, List[str]] = defaultdict(list)

        traceConfigByModelKey = defaultdict(list)
        for traceConfig in newTraceConfigs:
            traceConfigByModelKey[traceConfig.modelSetKey].append(traceConfig)

            modelSetId = modelSetIdByKey.get(traceConfig.modelSetKey)
            insertedOrCreated[modelSetId].append(traceConfig.importGroupHash)

        for modelSetKey, traceConfigs in traceConfigByModelKey.items():
            modelSetId = modelSetIdByKey.get(modelSetKey)
            if modelSetId is None:
                modelSetId = _makeModelSet(modelSetKey)
                modelSetIdByKey[modelSetKey] = modelSetId

            _insertOrUpdateObjects(traceConfigs, modelSetId)

        return insertedOrCreated

    except Exception as e:
        logger.debug("Retrying import graphDb objects, %s", e)
        raise self.retry(exc=e, countdown=3)


def _validateNewTraceConfigs(
        newTraceConfigs: List[GraphDbImportTraceConfigTuple]) -> None:
    for traceConfig in newTraceConfigs:
        if not traceConfig.key:
            raise Exception("key is empty for %s" % traceConfig)

        if not traceConfig.name:
            raise Exception("name is empty for %s" % traceConfig)

        if not traceConfig.modelSetKey:
            raise Exception("modelSetKey is empty for %s" % traceConfig)


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


def _insertOrUpdateObjects(newTraceConfigs: List[GraphDbImportTraceConfigTuple],
                           modelSetId: int) -> None:
    """ Insert or Update Objects

    1) Find objects and update them
    2) Insert object if the are missing

    """

    traceConfigTable = GraphDbTraceConfig.__table__

    startTime = datetime.now(pytz.utc)

    dbSession = CeleryDbConn.getDbSession()
    transaction = dbSession.begin()

    try:
        importHashSet = {i.importGroupHash for i in newTraceConfigs}

        dbSession.execute(
            traceConfigTable.delete(
                traceConfigTable.c.importGroupHash.in_(importHashSet))
        )

        # Create state arrays
        inserts = []

        # Create the DB Orm objects to insert
        for importTraceConfig in newTraceConfigs:
            dbSession.add(GraphDbTraceConfig().fromTuple(importTraceConfig,modelSetId))

        transaction.commit()

        logger.debug("Inserted %s trace configs in %s",
                     len(inserts),
                     (datetime.now(pytz.utc) - startTime))

    except Exception:
        transaction.rollback()
        raise


    finally:
        dbSession.close()
