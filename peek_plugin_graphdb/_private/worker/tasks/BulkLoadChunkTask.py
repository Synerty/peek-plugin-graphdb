import logging
from typing import List

from sqlalchemy import select
from txcelery.defer import DeferrableTask

from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_graphdb._private.storage.GraphDbItem import GraphDbItem
from peek_plugin_graphdb._private.worker.CeleryApp import celeryApp
from peek_plugin_graphdb.tuples.GraphDbDisplayValueTuple import GraphDbDisplayValueTuple

logger = logging.getLogger(__name__)


@DeferrableTask
@celeryApp.task(bind=True)
def qryChunkInWorker(self, offset, limit) -> List[GraphDbDisplayValueTuple]:
    """ Query Chunk

    This returns a chunk of GraphDB items from the database

    :param self: A celery reference to this task
    :param offset: The offset of the chunk
    :param limit: An encoded payload containing the updates
    :returns: List[GraphDbDisplayValueTuple] serialised in a payload json
    """

    table = GraphDbItem.__table__
    cols = [table.c.key, table.c.dataType, table.c.rawValue, table.c.displayValue]

    session = CeleryDbConn.getDbSession()
    try:
        result = session.execute(select(cols)
                                 .order_by(table.c.id)
                                 .offset(offset)
                                 .limit(limit))

        return [GraphDbDisplayValueTuple(
            key=o.key, dataType=o.dataType,
            rawValue=o.rawValue, displayValue=o.displayValue) for o in result.fetchall()]

    finally:
        session.close()
