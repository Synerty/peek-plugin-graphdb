import logging
from datetime import datetime
from typing import List, Dict

from sqlalchemy import not_
from sqlalchemy.sql.expression import select
from txcelery.defer import DeferrableTask

from peek_plugin_base.storage.StorageUtil import makeCoreValuesSubqueryCondition
from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_graphdb._private.storage.GraphDbEdge import GraphDbEdge
from peek_plugin_graphdb._private.storage.GraphDbModelSet import \
    getOrCreateGraphDbModelSet
from peek_plugin_graphdb._private.storage.GraphDbVertex import GraphDbVertex
from peek_plugin_graphdb._private.worker.CeleryApp import celeryApp
from peek_plugin_graphdb.tuples.GraphDbImportEdgeTuple import GraphDbImportEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbImportVertexTuple import GraphDbImportVertexTuple

logger = logging.getLogger(__name__)

vertexTable = GraphDbVertex.__table__
edgeTable = GraphDbEdge.__table__

CHUNK_SIZE = 1000


@DeferrableTask
@celeryApp.task(bind=True)
def importGraphSegment(self, modelSetName: str, segmentHash: str,
                       vertices: List[GraphDbImportVertexTuple],
                       edges: List[GraphDbImportEdgeTuple]) -> List[str]:
    """ Import Graph Segment

    Import a new segment of the Graph, replacing existing vertices and edges with the
    same segmentHash.

    :param self: A reference to the bound celery task
    :param modelSetName:  The name of the model set for the live db.
    :param segmentHash: The unique segment hash for the graph segment being imported.
    :param vertices: A list of vertices to import / update.
    :param edges: A list of edges to import / update.


    1) Search for nodes that have other segments edges connected to them.

    """

    startTime = datetime.utcnow()

    session = CeleryDbConn.getDbSession()
    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()

    try:
        vertexKeys = [v.key for v in vertices]

        modelSet = getOrCreateGraphDbModelSet(session, modelSetName)

        _deleteSegment(conn, segmentHash)

        existingVerticesIdByKey = _findExistingVertices(
            engine, conn, modelSet.id, vertexKeys,
        )

        vertexInserts = []
        edgeInserts = []

        for newVertex in vertices:
            if newVertex.key in existingVerticesIdByKey:
                continue

            vertexInserts.append(dict(
                modelSetId=modelSet.id,
                key=newVertex.key,
                propsJson=newVertex.propsJson
            ))

            newKeys.append(newItem.key)

        if vertexInserts:
            conn.execute(vertexTable.__table__.insert(), vertexInserts)

        if edgeInserts:
            conn.execute(edgeTable.__table__.insert(), edgeInserts)

        transaction.commit()
        logger.info("Inserted / Updated %s GraphDbItems, %s already existed, in %s",
                    len(inserts), len(existingKeys), (datetime.utcnow() - startTime))

        return newKeys

    except Exception as e:
        transaction.rollback()
        logger.warning("Task failed, but it will retry. %s", e)
        raise self.retry(exc=e, countdown=10)

    finally:
        conn.close()
        session.close()


def _deleteSegment(conn, segmentHash: str):
    # Delete all edges in this segment
    conn.execute(
        edgeTable.delete()
            .where(edgeTable.c.segmentHash == segmentHash))

    # Delete all vertices that no longer have an edge connected to them.
    # NOTE: This deletes ALL nodes that don't have edges connected to them
    conn.execute(
        vertexTable.delete()
            .where(not_(vertexTable.c.id.in_(select([edgeTable.c.srcId]))))
            .where(not_(vertexTable.c.id.in_(select([edgeTable.c.dstId]))))

    )


def _findExistingVertices(engine, conn, modelSetId: int,
                          vertexKeys: List[str]) -> Dict[str, int]:
    result = {}

    # Query for existing vertices, in 1000 chinks
    offset = 0
    while True:
        chunk = vertexKeys[offset:offset + CHUNK_SIZE]
        if not chunk:
            break
        offset += CHUNK_SIZE

        stmt = (
            select([vertexTable.c.key])
                .where(vertexTable.c.modelSetId == modelSetId)
                .where(makeCoreValuesSubqueryCondition(engine, vertexTable.c.key, chunk)
                       )
        )

        result = conn.execute(stmt)

        result.update({o[0]: o[1] for o in result.fetchall()})

    return result
