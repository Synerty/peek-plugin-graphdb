import logging
import ujson as json
from typing import Dict, List

from collections import namedtuple
from sqlalchemy import bindparam
from sqlalchemy.orm import Session
from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger

from peek_plugin_base.storage.DbConnection import DbSessionCreator, DeclarativeIdCreator
from peek_plugin_base.storage.StorageUtil import makeCoreValuesSubqueryCondition
from peek_plugin_graphdb._private.server.api.GraphDbReadApi import GraphDbReadApi
from peek_plugin_graphdb._private.server.graph.GrpahModelController import GraphModel
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
    """ GraphDb Import Controller
    """

    def __init__(self, graphModel: GraphModel,
                 readApi: GraphDbReadApi,
                 dbSessionCreator: DbSessionCreator,
                 dbIdCreator: DeclarativeIdCreator):
        self._graphModel = graphModel
        self._dbSessionCreator = dbSessionCreator
        self._dbIdCreator = dbIdCreator
        self._readApi = readApi

        self._modelSetId = self._graphModel.modelSet().id
        self._modelSetKey = self._graphModel.modelSet().key

        self._addedVertices: List[GraphDbVertexTuple] = []
        self._deletedVertexKeys: List[str] = []
        self._updatedVertexAttrs: List[VertexAttrUpdate] = []
        self._updatedVertexProps: List[VertexPropUpdate] = []

        self._addedEdges: List[GraphDbEdgeTuple] = []
        self._deletedEdgeKeys: List[str] = []
        self._updatedEdgeProps: List[EdgePropUpdate] = []

        self._saved = False

    @inlineCallbacks
    def save(self):
        self._saved = True

        yield self._setNewObjectIds()

        # Perform the DB saves
        yield self._saveToDb()

        # Save to the model
        self._applyEdgeDeletes()
        self._applyVertexDeletes()
        self._applyVertexAdditions()

    @deferToThreadWrapWithLogger(logger)
    def _saveToDb(self):
        ormSession = self._dbSessionCreator()
        try:
            self._saveEdgeDeletes(ormSession)
            self._saveVertexDeletes(ormSession)
            self._saveVertexAdditions(ormSession)

        finally:
            ormSession.close()

    # ---------------
    # Vertex update methods

    def deleteVertex(self, vertexKey: str):
        assert not self._saved, "Context can not be updated after a save"
        self._deletedVertexKeys.append(vertexKey)

    def updateVertexAttributes(self, vertexKey, updates: Dict[str, str]):
        assert not self._saved, "Context can not be updated after a save"
        assert updates, "No updates provided for this vertex"
        self._updatedVertexAttrs.append(VertexAttrUpdate(vertexKey, updates))

    def updateVertexProps(self, vertexKey, newProps: Dict):
        assert not self._saved, "Context can not be updated after a save"
        assert newProps, "No props provided for this vertex"
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
        assert newProps, "No props provided for this edge"
        self._updatedEdgeProps.append(EdgePropUpdate(edgeKey, newProps))

    # ---------------
    # Assign DB ids to new items

    @inlineCallbacks
    def _setNewObjectIds(self):

        # Prefetch IDs for the vertexes and assign them
        vertexIdGen = yield self._dbIdCreator(GraphDbVertex, len(self._addedVertices))
        for vertex in self._addedVertices:
            vertex.id = next(vertexIdGen)

        # Prefetch IDs for the edges and assign them
        edgeIdGen = yield self._dbIdCreator(GraphDbEdge, len(self._addedEdges))
        for edge in self._addedEdges:
            edge.id = next(edgeIdGen)

            # Resolve the vertex IDs
            edge.srcId = edge.src.id
            edge.dstId = edge.dst.id

    # ---------------
    # Delete Edge Methods

    def _saveEdgeDeletes(self, ormSession: Session):
        stmt = (
            edgeTable.delete()
                .where(edgeTable.c.modelSetId == self._modelSetId)
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

            self._readApi.edgeDeletionObservable(self._modelSetKey).on_next(edge)

    # ---------------
    # Delete Vertex Methods

    def _saveVertexDeletes(self, ormSession):
        stmt = (
            edgeTable.delete()
                .where(vertexTable.c.modelSetId == self._modelSetId)
                .where(makeCoreValuesSubqueryCondition(
                ormSession.bind, vertexTable.c.key, self._deletedVertexKeys
            ))
        )
        ormSession.execute(stmt)

    def _applyVertexDeletes(self):
        for vertexKey in self._deletedVertexKeys:
            vertex = self._graphModel._vertexByKey.pop(vertexKey, None)
            del self._graphModel._vertexById[vertex.id]

            self._readApi.vertexDeletionObservable(self._modelSetKey).on_next(vertex)

    # ---------------
    # Add Vertex Methods

    def _saveVertexAdditions(self, ormSession: Session):
        if not self._addedVertices:
            return

        inserts = []
        for t in self._addedVertices:
            insert = t.tupleToSqlaBulkInsertDict()
            insert["modelSetId"] = self._modelSetId

            props = insert.pop("props")
            if props:
                insert["propsJson"] = json.dumps(insert.pop("props"))
            else:
                insert["propsJson"] = None

        ormSession.execute(vertexTable.insert(), inserts)

    def _applyVertexAdditions(self):
        for vertex in self._addedVertices:
            self._graphModel._indexVertex(vertex)

            self._readApi.vertexAdditionObservable(self._modelSetKey).on_next(vertex)

    # ---------------
    # Add Vertex Methods

    def _saveEdgeAdditions(self, ormSession: Session):
        if not self._addedEdges:
            return

        inserts = []
        for t in self._addedEdges:
            insert = t.tupleToSqlaBulkInsertDict()
            insert["modelSetId"] = self._modelSetId

            props = insert.pop("props")
            if props:
                insert["propsJson"] = json.dumps(insert.pop("props"))
            else:
                insert["propsJson"] = None

        ormSession.execute(edgeTable.insert(), inserts)

    def _applyEdgeAdditions(self):
        for edge in self._addedEdges:
            self._graphModel._indexEdge(edge)
            self._graphModel._linkEdge(edge)

            self._readApi.edgeAdditionObservable(self._modelSetKey).on_next(edge)

    # ---------------
    # Update Vertex Attributes

    def _saveVertexAttrUpdates(self, ormSession):
        if not self._updatedVertexAttrs:
            return
        
        stmt = (
            vertexTable.update()
                .where(vertexTable.c.id == bindparam('_id'))
                .values(name=bindparam('_name'), desc=bindparam('_desc'))
        )

        updates = []
        for vertexKey, updates in self._updatedVertexAttrs:
            vertex = self._graphModel.vertexForKey(vertexKey)
            if not vertex:
                raise Exception("_saveEdgePropUpdates, edge doesn't exist")

            updates.append(
                {
                    'id': vertex.id,
                    '_name': updates.pop('name', vertex.name),
                    '_desc': updates.pop('desc', vertex.desc)
                }
            )

        ormSession.execute(stmt, updates)

    def _applyVertexAttrUpdates(self):
        for vertexKey, updates in self._updatedVertexAttrs:
            vertex = self._graphModel.vertexForKey(vertexKey)

            for key, value in updates.items():
                setattr(vertex, key, value)

            self._readApi.vertexAttrUpdateObservable(self._modelSetKey).on_next(vertex)

    # ---------------
    # Update Vertex Properties

    def _saveVertexPropUpdates(self, ormSession):
        if not self._updatedVertexProps:
            return
        
        stmt = (
            vertexTable.update()
                .where(vertexTable.c.id == bindparam('_id'))
                .values(propsJson=bindparam('_propsJson'))
        )

        updates = []
        for vertexKey, props in self._updatedVertexProps:
            vertex = self._graphModel.vertexForKey(vertexKey)
            if not vertex:
                raise Exception("_saveEdgePropUpdates, edge doesn't exist")

            propsJson = None
            if props:
                propsJson = json.dumps(props)

            updates.append({'id': vertex.id, '_propsJson': propsJson})

        ormSession.execute(stmt, updates)

    def _applyVertexPropUpdates(self):
        for vertexKey, props in self._updatedVertexProps:
            vertex = self._graphModel.vertexForKey(vertexKey)
            vertex.props = props

            self._readApi.vertexPropUpdateObservable(self._modelSetKey).on_next(vertex)

    # ---------------
    # Update Edge Properties

    def _saveEdgePropUpdates(self, ormSession):
        if not self._updatedEdgeProps:
            return

        stmt = (
            edgeTable.update()
                .where(edgeTable.c.id == bindparam('_id'))
                .values(propsJson=bindparam('_propsJson'))
        )

        updates = []
        for edgeKey, props in self._updatedEdgeProps:
            edge = self._graphModel.edgeForKey(edgeKey)
            if not edge:
                raise Exception("_saveEdgePropUpdates, edge doesn't exist")

            propsJson = None
            if props:
                propsJson = json.dumps(props)

            updates.append({'id': edge.id, '_propsJson': propsJson})

        ormSession.execute(stmt, updates)

    def _applyEdgePropUpdates(self):
        for edgeKey, props in self._updatedEdgeProps:
            edge = self._graphModel.edgeForKey(edgeKey)
            edge.props = props

            self._readApi.edgePropUpdateObservable(self._modelSetKey).on_next(edge)
