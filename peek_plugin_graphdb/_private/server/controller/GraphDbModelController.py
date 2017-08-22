import logging
from ujson import json

from sqlalchemy import select
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger

from peek_plugin_graphdb._private.storage.GraphDbEdge import GraphDbEdge
from peek_plugin_graphdb._private.storage.GraphDbVertex import GraphDbVertex
from peek_plugin_graphdb.tuples.GraphDbEdgeTuple import GraphDbEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbVertexTuple import GraphDbVertexTuple

logger = logging.getLogger(__name__)


class GraphDbModelController(object):
    def __init__(self, dbSessionCreator, modelSetId: int):
        self._dbSessionCreator = dbSessionCreator
        self._modelSetId = modelSetId

        self._verticesByKey = {}
        self._verticesById = {}

    def start(self) -> Deferred:
        return self._loadModel()

    def shutdown(self):
        del self._verticesByKey
        del self._verticesById

    @deferToThreadWrapWithLogger(logger)
    def _loadModel(self):
        vertexTable = GraphDbVertex.__table__
        edgeTable = GraphDbEdge.__table__

        ormSession = self._dbSessionCreator()
        try:
            # Load vertices
            stmt = (
                select([vertexTable.c.id,
                        vertexTable.c.key,
                        vertexTable.c.name,
                        vertexTable.c.desc,
                        vertexTable.c.propsJson])
                    .where(vertexTable.c.modelSetId == self._modelSetId)
            )

            result = ormSession.execute(stmt)

            chunk = result.fetchmany(5000)
            while chunk:
                for item in chunk:
                    vertex = GraphDbVertexTuple(
                        id=item.id,
                        key=item.key,
                        name=item.name,
                        desc=item.desc,
                        props=json.loads(item.propsJson)
                    )
                    self._verticesByKey[vertex.id] = vertex
                    self._verticesByKey[vertex.key] = vertex

            # Load edges
            stmt = (
                select([edgeTable.c.id,
                        edgeTable.c.srcId,
                        edgeTable.c.dstId,
                        edgeTable.c.propsJson])
                    .where(edgeTable.c.modelSetId == self._modelSetId)
            )

            result = ormSession.execute(stmt)

            chunk = result.fetchmany(5000)
            while chunk:
                for item in chunk:
                    src = self._verticesById.get(item.srcId)
                    if not src:
                        logger.error("ModelSet %s is missing vertex %s for edge %s",
                                     self._modelSetId, item.srcId, item.id)
                        continue

                    dst = self._verticesById.get(item.dstId)
                    if not dst:
                        logger.error("ModelSet %s is missing vertex %s for edge %s",
                                     self._modelSetId, item.dstId, item.id)
                        continue

                    edge = GraphDbEdgeTuple(
                        id=item.id,
                        srcId=item.srcId,
                        dstId=item.dstId,
                        src=src,
                        dst=dst,
                        props=json.loads(item.propsJson)
                    )

                    src.edges = src.edges + (edge,)
                    dst.edges = dst.edges + (edge,)


        finally:
            ormSession.close()
