import logging
from typing import Dict, List

from collections import namedtuple
from sqlalchemy.orm import Session
from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger

from peek_plugin_base.storage.DbConnection import DbSessionCreator, DeclarativeIdCreator
from peek_plugin_base.storage.StorageUtil import makeCoreValuesSubqueryCondition
from peek_plugin_graphdb._private.server.GraphDBReadApi import GraphDBReadApi
from peek_plugin_graphdb._private.server.graph.GraphModel import GraphModel
from peek_plugin_graphdb._private.storage.GraphDbEdge import GraphDbEdge
from peek_plugin_graphdb._private.storage.GraphDbVertex import GraphDbVertex
from peek_plugin_graphdb.tuples.GraphDbEdgeTuple import GraphDbEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbVertexTuple import GraphDbVertexTuple

logger = logging.getLogger(__name__)

vertexTable = GraphDbVertex.__table__
edgeTable = GraphDbEdge.__table__

VertexAttrUpdate = namedtuple("VertexAttrUpdate", ("key", "updates"))
VertexPropUpdate = namedtuple("VertexPropUpdate", ("key", "props"))
EdgePropUpdate = namedtuple("EdgePropUpdate", ("key", "props"))


class GraphUpdateContext:
    """ GraphDB Import Controller
    """

    def __init__(self, graphModel: GraphModel,
                 readApi: GraphDBReadApi,
                 dbSessionCreator: DbSessionCreator,
                 dbIdCreator: DeclarativeIdCreator):
        self._graphModel = graphModel
        self._dbSessionCreator = dbSessionCreator
        self._dbIdCreator = dbIdCreator
        self._readApi = readApi

        self._addedVertices: List[GraphDbVertexTuple] = []
        self._deletedVertexKeys: List[str] = []
        self._updatedVertexAttributes: List[VertexAttrUpdate] = []
        self._updatedVertexProps: List[VertexPropUpdate] = []

        self._addedEdges: List[GraphDbEdgeTuple] = []
        self._deletedEdgeKeys: List[str] = []
        self._updatedEdgesProps: List[EdgePropUpdate] = []

        self._saved = False

    @inlineCallbacks
    def save(self):
        self._saved = True

        # Prefetch IDs for the vertexes and assign them
        vertexIdGen = yield self._dbIdCreator(GraphDbVertex, len(self._addedVertices))
        for vertex in self._addedVertices:
            vertex.id = next(vertexIdGen)

        # Prefetch IDs for the edges and assign them
        edgeIdGen = yield self._dbIdCreator(GraphDbEdge, len(self._addedEdges))
        for edge in self._addedEdges:
            edge.id = next(edgeIdGen)

        # Perform the DB saves
        yield self._saveToDb()

        # Save to the model
        self._applyEdgeDeletes()
        self._applyVertexDeletes()
        self._applyVertexAdditions()

    @deferToThreadWrapWithLogger(logger)
    def _saveToDb(self):
        modelSetId = self._graphModel.modelSet().id
        ormSession = self._dbSessionCreator()
        try:
            self._saveEdgeDeletes(ormSession, modelSetId)
            self._saveVertexDeletes(ormSession, modelSetId)
            self._saveVertexAdditions(ormSession, modelSetId)

        finally:
            ormSession.close()

    # ---------------
    # Vertex update methods

    def deleteVertex(self, vertexKey: str):
        assert not self._saved, "Context can not be updated after a save"
        self._deletedVertexKeys.append(vertexKey)

    def updateVertexAttributes(self, vertexKey, updates: Dict[str, str]):
        assert not self._saved, "Context can not be updated after a save"
        self._updatedVertexAttributes.append(VertexAttrUpdate(vertexKey, updates))

    def updateVertexProps(self, vertexKey, newProps: Dict):
        assert not self._saved, "Context can not be updated after a save"
        self._updatedVertexProps.append(VertexPropUpdate(vertexKey, newProps))

    def addVertex(self, vertex: GraphDbVertexTuple):
        assert not self._saved, "Context can not be updated after a save"
        self._addedVertices.append(vertex)

    # ---------------
    # Edge update methods

    def deleteEdge(self, edgeKey: str):
        assert not self._saved, "Context can not be updated after a save"
        self._deletedEdgeKeys.append(edgeKey)

    def addEdge(self, edge: GraphDbEdgeTuple):
        assert not self._saved, "Context can not be updated after a save"
        self._addedEdges.append(edge)

    def updateEdgeProps(self, edgeKey, newProps: Dict):
        assert not self._saved, "Context can not be updated after a save"
        self._updatedEdgesProps.append(EdgePropUpdate(edgeKey, newProps))

    # ---------------
    # Delete Edge Methods

    def _saveEdgeDeletes(self, ormSession: Session, modelSetId: str):
        stmt = (
            edgeTable.delete()
                .where(edgeTable.c.modelSetId == modelSetId)
                .where(makeCoreValuesSubqueryCondition(
                ormSession.bind, edgeTable.c.key, self._deletedEdgeKeys
            ))
        )
        ormSession.execute(stmt)

    def _applyEdgeDeletes(self):
        for edgeKey in self._deletedEdgeKeys:
            # Unindex the edge
            edge = self._graphModel._edgeByKey.pop(edgeKey, None)
            if not edge:
                continue
            del self._graphModel._edgeBySrcIdDstId[(edge.srcId, edge.dstId)]
            del self._graphModel._edgeBySrcKeyDstKey[(edge.srcKey, edge.dstKey)]

            arr = self._graphModel._edgesBySegmentHash[edge.segmentHash]
            arr.remove(edge)
            if not arr:
                del self._graphModel._edgesBySegmentHash[edge.segmentHash]

            # Unlink the edge
            edge.src.edges = tuple(set(edge.src.edges) - {edge})
            edge.dst.edges = tuple(set(edge.dst.edges) - {edge})

    # ---------------
    # Delete Vertex Methods

    def _applyVertexDeletes(self, ormSession, modelSetId):
        stmt = (
            edgeTable.delete()
                .where(vertexTable.c.modelSetId == modelSetId)
                .where(makeCoreValuesSubqueryCondition(
                ormSession.bind, vertexTable.c.key, self._deletedVertexKeys
            ))
        )
        ormSession.execute(stmt)

    def _saveVertexDeletes(self):
        for vertexKey in self._deletedVertexKeys:
            vertex = self._graphModel._vertexByKey.pop(vertexKey, None)
            del self._graphModel._vertexById[vertex.id]

    # ---------------
    # Add Vertex Methods

    def _saveVertexAdditions(self, ormSession: Session, modelSetId: str):
        if not self._addedVertices:
            return

        inserts = [t.tupleToSqlaBulkInsertDict() for t in self._addedVertices]
        ormSession.execute(vertexTable.__table__.insert(), inserts)

    def _applyVertexAdditions(self):
        for vertex in self._addedVertices:
            self._graphModel._indexVertex(vertex)
