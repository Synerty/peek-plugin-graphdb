import logging
from typing import List, Optional
from ujson import json

from collections import defaultdict
from sqlalchemy import select
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger

from peek_plugin_graphdb._private.server.GraphDBReadApi import GraphDBReadApi
from peek_plugin_graphdb._private.server.graph.GraphUpdateContext import \
    GraphUpdateContext
from peek_plugin_graphdb._private.storage.GraphDbEdge import GraphDbEdge
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from peek_plugin_graphdb._private.storage.GraphDbVertex import GraphDbVertex
from peek_plugin_graphdb.tuples.GraphDbEdgeTuple import GraphDbEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbVertexTuple import GraphDbVertexTuple

logger = logging.getLogger(__name__)


class GraphModel(object):
    def __init__(self, dbSessionCreator,
                 readApi: GraphDBReadApi,
                 modelSet: GraphDbModelSet):

        self._dbSessionCreator = dbSessionCreator
        self._readApi = readApi
        self._modelSet = modelSet

        self._verticesByKey = {}
        self._verticesById = {}
        self._edgesBySegmentHash = defaultdict(list)
        self._edgeBySrcIdDstId = {}
        self._edgeBySrcKeyDstKey = {}

    # ---------------
    # Accessor methods
    
    def edgesForSegmentHash(self, segmentHash: str) -> List[GraphDbEdgeTuple]:
        return list(self._edgesBySegmentHash.get(segmentHash, []))

    def edgeForSrcKeyDstKey(self, srcKey: str, dstKey:str) -> Optional[GraphDbEdgeTuple]:
        return self._edgeBySrcKeyDstKey.get((srcKey, dstKey))

    def edgeForSrcIdDstId(self, srcId: int, dstId:int) -> Optional[GraphDbEdgeTuple]:
        return self._edgeBySrcKeyDstKey.get((srcId, dstId))

    def vertexForKey(self, key: str) -> GraphDbVertexTuple:
        return self._verticesByKey.get(key)

    def vertexForId(self, id: int) -> GraphDbVertexTuple:
        return self._verticesById.get(id)

    def newUpdateContext(self) -> GraphUpdateContext:
        return GraphUpdateContext(self, self._readApi, self._dbSessionCreator)

    # ---------------
    # Start/Stop methods

    def start(self) -> Deferred:
        return self._loadModel()

    def shutdown(self):
        del self._verticesByKey
        del self._verticesById
        del self._edgesBySegmentHash
        del self._edgeBySrcIdDstId
        del self._edgeBySrcKeyDstKey

    # ---------------
    # Load methods

    @deferToThreadWrapWithLogger(logger)
    def _loadModel(self) -> Deferred:
        vertexTable = GraphDbVertex.__table__
        edgeTable = GraphDbEdge.__table__

        ormSession = self._dbSessionCreator()
        try:
            # Load vertices ---------------
            stmt = (
                select([vertexTable.c.id,
                        vertexTable.c.key,
                        vertexTable.c.name,
                        vertexTable.c.desc,
                        vertexTable.c.propsJson])
                    .where(vertexTable.c.modelSetId == self._modelSet.id)
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

            # Load edges ---------------
            stmt = (
                select([edgeTable.c.id,
                        edgeTable.c.segmentHash,
                        edgeTable.c.srcId,
                        edgeTable.c.dstId,
                        edgeTable.c.propsJson])
                    .where(edgeTable.c.modelSetId == self._modelSet.id)
            )

            result = ormSession.execute(stmt)

            chunk = result.fetchmany(5000)
            while chunk:
                for item in chunk:
                    src = self._verticesById.get(item.srcId)
                    if not src:
                        logger.error("ModelSet %s is missing vertex %s for edge %s",
                                     self._modelSet.id, item.srcId, item.id)
                        continue

                    dst = self._verticesById.get(item.dstId)
                    if not dst:
                        logger.error("ModelSet %s is missing vertex %s for edge %s",
                                     self._modelSet.id, item.dstId, item.id)
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
                    self._edgesBySegmentHash[item.segmentHash].append(edge)
                    self._edgeBySrcKeyDstKey[(src.key, dst.key)] = edge

                chunk = result.fetchmany(5000)

        finally:
            ormSession.close()
