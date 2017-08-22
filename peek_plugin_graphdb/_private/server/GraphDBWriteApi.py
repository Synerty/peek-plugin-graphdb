import logging
from typing import List

from twisted.internet import defer
from twisted.internet.defer import Deferred

from peek_plugin_graphdb._private.server.controller.MainController import MainController
from peek_plugin_graphdb._private.server.graph.GraphSegmentImporter import \
    GraphSegmentImporter
from peek_plugin_graphdb.server.GraphDBWriteApiABC import GraphDBWriteApiABC
from peek_plugin_graphdb.tuples.GraphDbImportEdgeTuple import GraphDbImportEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbImportVertexTuple import GraphDbImportVertexTuple

logger = logging.getLogger(__name__)


class GraphDBWriteApi(GraphDBWriteApiABC):
    def __init__(self, mainController: MainController):
        self._mainController = mainController

    def shutdown(self):
        pass

    def importGraphSegment(self, modelSetKey: str, segmentHash: str,
                           vertices: List[GraphDbImportVertexTuple],
                           edges: List[GraphDbImportEdgeTuple]) -> Deferred:

        if not vertices and not edges:
            return defer.succeed(True)

        self._mainController.graphForModelSetKey(modelSetKey)

        return self._graphDbImportController.importGraphSegment(
            modelSetKey=modelSetKey,
            segmentHash=segmentHash,
            vertices=vertices,
            edges=edges
        )
