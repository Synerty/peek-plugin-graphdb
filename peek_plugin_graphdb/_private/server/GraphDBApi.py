from peek_plugin_graphdb._private.server.GraphDBReadApi import GraphDBReadApi
from peek_plugin_graphdb._private.server.GraphDBWriteApi import GraphDBWriteApi
from peek_plugin_graphdb._private.server.controller.MainController import MainController
from peek_plugin_graphdb._private.server.graph.GraphSegmentImporter import \
    GraphSegmentImporter
from peek_plugin_graphdb.server.GraphDBApiABC import GraphDBApiABC
from peek_plugin_graphdb.server.GraphDBReadApiABC import GraphDBReadApiABC
from peek_plugin_graphdb.server.GraphDBWriteApiABC import GraphDBWriteApiABC


class GraphDBApi(GraphDBApiABC):
    def __init__(self, mainController: MainController):
        self._readApi = GraphDBReadApi(
            mainController=mainController
        )

        self._writeApi = GraphDBWriteApi(
            mainController=mainController
        )

    def shutdown(self):
        self._readApi.shutdown()
        self._writeApi.shutdown()

        self._readApi = None
        self._writeApi = None

    @property
    def writeApi(self) -> GraphDBWriteApiABC:
        return self._writeApi

    @property
    def readApi(self) -> GraphDBReadApiABC:
        return self._readApi
