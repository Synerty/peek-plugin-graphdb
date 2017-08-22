import logging
from typing import Dict

from peek_plugin_graphdb._private.server.GraphDBReadApi import GraphDBReadApi
from peek_plugin_graphdb._private.server.graph.GraphModel import GraphModel
from peek_plugin_graphdb.tuples.GraphDbEdgeTuple import GraphDbEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbVertexTuple import GraphDbVertexTuple

logger = logging.getLogger(__name__)


class GraphUpdateContext:
    """ GraphDB Import Controller
    """

    def __init__(self, graphModel: GraphModel,
                 readApi: GraphDBReadApi,
                 dbSessionCreator):
        self._graphModel = graphModel
        self._dbSessionCreator = dbSessionCreator
        self._readApi = readApi

        self._addedVertices = []
        self._deletedVertices = []
        self._updatedVertexAttributes = []
        self._updatedVertexProps = []

        self._addedEdges = []
        self._deletedEdges = []
        self._updatedEdgesProps = []

    def save(self):
        raise NotImplementedError()

    # ---------------
    # Vertex update methods

    def deleteVertex(self, vertexKey: str):
        pass

    def updateVertexAttributes(self, vertexKey, updates: Dict[str, str]):
        pass

    def updateVertexProps(self, vertexKey, newProps: Dict):
        pass

    def addVertex(self, vertex: GraphDbVertexTuple):
        pass

    # ---------------
    # Edge update methods

    def deleteEdge(self, edgeKey: str):
        pass

    def addEdge(self, edge: GraphDbEdgeTuple):
        pass

    def updateEdgeProps(self, edgeKey, newProps: Dict):
        pass
