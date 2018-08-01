from peek_plugin_graphdb._private.server.GraphDbReadApi import GraphDbReadApi
from peek_plugin_graphdb._private.server.GraphDbWriteApi import GraphDbWriteApi
from peek_plugin_graphdb._private.server.controller.MainController import MainController
from peek_plugin_graphdb._private.server.graph.GraphSegmentImporter import \
    GraphSegmentImporter
from peek_plugin_graphdb.server.GraphDbApiABC import GraphDbApiABC
from peek_plugin_graphdb.server.GraphDbReadApiABC import GraphDbReadApiABC
from peek_plugin_graphdb.server.GraphDbWriteApiABC import GraphDbWriteApiABC


class GraphDbApi(GraphDbApiABC):
    def __init__(self, mainController: MainController):
        self._readApi = GraphDbReadApi(
            mainController=mainController
        )

        self._writeApi = GraphDbWriteApi(
            mainController=mainController
        )

    def shutdown(self):
        self._readApi.shutdown()
        self._writeApi.shutdown()

        self._readApi = None
        self._writeApi = None

    @property
    def writeApi(self) -> GraphDbWriteApiABC:
        return self._writeApi

    @property
    def readApi(self) -> GraphDbReadApiABC:
        return self._readApi
