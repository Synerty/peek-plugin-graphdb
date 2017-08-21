import logging
from datetime import datetime
from typing import List

from sqlalchemy.sql.expression import select
from txcelery.defer import DeferrableTask

from peek_plugin_base.storage.StorageUtil import makeCoreValuesSubqueryCondition
from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_graphdb._private.storage.GraphDbItem import GraphDbItem
from peek_plugin_graphdb._private.storage.GraphDbModelSet import getOrCreateGraphDbModelSet
from peek_plugin_graphdb._private.worker.CeleryApp import celeryApp
from peek_plugin_graphdb.tuples.ImportGraphDbItemTuple import ImportGraphDbItemTuple

logger = logging.getLogger(__name__)


@DeferrableTask
@celeryApp.task(bind=True)
def importGraphDbItems(self, modelSetName: str,
                      newItems: List[ImportGraphDbItemTuple]) -> List[str]:
    """ Compile Grids Task

    :param self: A celery reference to this task
    :param modelSetName: The model set name
    :param newItems: The list of new items
    :returns: A list of grid keys that have been updated.
    """

    startTime = datetime.utcnow()

    session = CeleryDbConn.getDbSession()
    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()

    graphDbTable = GraphDbItem.__table__
    try:

        graphDbModelSet = getOrCreateGraphDbModelSet(session, modelSetName)

        # This will remove duplicates
        itemsByKey = {i.key: i for i in newItems}

        allKeys = list(itemsByKey)
        existingKeys = set()

        # Query for existing keys, in 1000 chinks
        chunkSize = 1000
        offset = 0
        while True:
            chunk = allKeys[offset:offset + chunkSize]
            if not chunk:
                break
            offset += chunkSize
            stmt = (select([graphDbTable.c.key])
                    .where(graphDbTable.c.modelSetId == graphDbModelSet.id)
            .where(makeCoreValuesSubqueryCondition(
                engine, graphDbTable.c.key, chunk
            ))
            )

            result = conn.execute(stmt)

            existingKeys.update([o[0] for o in result.fetchall()])

        inserts = []
        newKeys = []

        for newItem in itemsByKey.values():
            if newItem.key in existingKeys:
                continue

            inserts.append(dict(
                modelSetId=graphDbModelSet.id,
                key=newItem.key,
                dataType=newItem.dataType,
                rawValue=newItem.rawValue,
                displayValue=newItem.displayValue,
                importHash=newItem.importHash
            ))

            newKeys.append(newItem.key)

        if not inserts:
            return []

        conn.execute(GraphDbItem.__table__.insert(), inserts)

        transaction.commit()
        logger.info("Inserted %s GraphDbItems, %s already existed, in %s",
                    len(inserts), len(existingKeys), (datetime.utcnow() - startTime))

        return newKeys

    except Exception as e:
        transaction.rollback()
        logger.warning("Task failed, but it will retry. %s", e)
        raise self.retry(exc=e, countdown=10)

    finally:
        conn.close()
        session.close()
