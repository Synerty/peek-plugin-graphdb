import logging
from typing import List, Optional, Tuple, Dict
import ujson as json

from collections import defaultdict
from sqlalchemy import select
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger

from peek_plugin_graphdb._private.server.api.GraphDbReadApi import GraphDbReadApi
from peek_plugin_graphdb._private.storage.GraphDbSegment import GraphDbSegment
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from peek_plugin_graphdb.tuples.GraphDbEdgeTuple import GraphDbEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbVertexTuple import GraphDbVertexTuple

logger = logging.getLogger(__name__)


class GraphModelInMem(object):
    def __init__(self, dbSessionCreator,
                 readApi: GraphDbReadApi,
                 modelSet: GraphDbModelSet):

        self._dbSessionCreator = dbSessionCreator
        self._readApi = readApi
        self._modelSet = modelSet

        self._vertexByKey: Dict[str, GraphDbVertexTuple] = {}
        self._vertexById: Dict[int, GraphDbVertexTuple] = {}
        self._edgesBySegmentHash: Dict[str, List[GraphDbEdgeTuple]] = defaultdict(list)
        self._edgeBySrcIdDstId: Dict[Tuple[int, int], GraphDbEdgeTuple] = {}
        self._edgeBySrcKeyDstKey: Dict[Tuple[str, str], GraphDbEdgeTuple] = {}
        self._edgeByKey: Dict[str, GraphDbEdgeTuple] = {}

        #: Common Strings, This is used to ensure we don't have multiple strings of the
        # same hash around, Python will just refernce the same string object.
        self._sharedStrings: Dict[str, str] = {}

    # ---------------
    # Accessor methods

    def edgesForSegmentHash(self, segmentHash: str) -> List[GraphDbEdgeTuple]:
        return list(self._edgesBySegmentHash.get(segmentHash, []))

    def edgeForSrcIdDstId(self, srcId: int, dstId: int) -> Optional[GraphDbEdgeTuple]:
        return self._edgeBySrcIdDstId.get((srcId, dstId))

    def edgeForSrcKeyDstKey(self, srcKey: str, dstKey: str) -> Optional[GraphDbEdgeTuple]:
        return self._edgeBySrcKeyDstKey.get((srcKey, dstKey))

    def edgeForKey(self, key: str) -> Optional[GraphDbEdgeTuple]:
        return self._edgeByKey.get(key)

    def vertexForKey(self, key: str) -> Optional[GraphDbVertexTuple]:
        return self._vertexByKey.get(key)

    def vertexForId(self, id: int) -> Optional[GraphDbVertexTuple]:
        return self._vertexById.get(id)

    def newUpdateContext(self) -> 'GraphUpdateContext':
        from peek_plugin_graphdb._private.server.graph.GraphUpdateContext import \
            GraphUpdateContext
        return GraphUpdateContext(self, self._readApi, self._dbSessionCreator)

    def newSegmentImporter(self) -> 'GraphSegmentImporter':
        from peek_plugin_graphdb._private.server.graph.GraphSegmentImporter import \
            GraphSegmentImporter
        return GraphSegmentImporter(self)

    def modelSet(self) -> GraphDbModelSet:
        return self._modelSet

    # ---------------
    # Start/Stop methods

    def start(self) -> Deferred:
        return self._loadModel()

    def shutdown(self):
        del self._vertexByKey
        del self._vertexById
        del self._edgesBySegmentHash
        del self._edgeBySrcIdDstId
        del self._edgeBySrcKeyDstKey
        del self._edgeByKey

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
                        key=item.key,
                        name=item.name,
                        desc=item.desc,
                        props=json.loads(item.propsJson)
                    )
                    self._indexVertex(vertex)

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
                    src = self._vertexById.get(item.srcId)
                    if not src:
                        logger.error("ModelSet %s is missing vertex %s for edge %s",
                                     self._modelSet.id, item.srcId, item.id)
                        continue

                    dst = self._vertexById.get(item.dstId)
                    if not dst:
                        logger.error("ModelSet %s is missing vertex %s for edge %s",
                                     self._modelSet.id, item.dstId, item.id)
                        continue

                    edge = GraphDbEdgeTuple(
                        srcId=item.srcId,
                        dstId=item.dstId,
                        segmentHash=self._makeSharedString(item.segmentHash),
                        src=src,
                        dst=dst,
                        props=json.loads(item.propsJson)
                    )
                    self._linkEdge(edge)
                    self._indexEdge(edge)

                chunk = result.fetchmany(5000)

        finally:
            ormSession.close()

    def _indexVertex(self, vertex: GraphDbVertexTuple):
        self._vertexByKey[vertex.id] = vertex
        self._vertexByKey[vertex.key] = vertex

    def _indexEdge(self, edge: GraphDbEdgeTuple):
        self._edgesBySegmentHash[edge.segmentHash].append(edge)
        self._edgeBySrcIdDstId[(edge.srcId, edge.dstId)] = edge
        self._edgeBySrcKeyDstKey[(edge.src.key, edge.dst.key)] = edge
        self._edgeByKey[edge.key] = edge

    def _linkEdge(self, edge: GraphDbEdgeTuple):
        edge.src.edges = edge.src.edges + (edge,)
        edge.dst.edges = edge.dst.edges + (edge,)

    def _makeSharedString(self, val):
        if val in self._sharedStrings:
            return self._sharedStrings[val]

        self._sharedStrings[val] = val
        return val
