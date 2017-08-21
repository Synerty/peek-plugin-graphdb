from peek_plugin_graphdb._private.server.GraphDBReadApi import GraphDBReadApi
from peek_plugin_graphdb._private.server.GraphDBWriteApi import GraphDBWriteApi
from peek_plugin_graphdb._private.server.controller.GraphDbController import \
    GraphDbController
from peek_plugin_graphdb._private.server.controller.GraphDbImportController import \
    GraphDbImportController
from peek_plugin_graphdb.server.GraphDBApiABC import GraphDBApiABC
from peek_plugin_graphdb.server.GraphDBReadApiABC import GraphDBReadApiABC
from peek_plugin_graphdb.server.GraphDBWriteApiABC import GraphDBWriteApiABC


class GraphDBApi(GraphDBApiABC):
    def __init__(self, graphDbController: GraphDbController,
                 graphDbImportController: GraphDbImportController,
                 dbSessionCreator,
                 dbEngine):
        self._readApi = GraphDBReadApi(graphDbController=graphDbController,
                                      dbSessionCreator=dbSessionCreator,
                                      dbEngine=dbEngine)
        self._writeApi = GraphDBWriteApi(graphDbController=graphDbController,
                                        graphDbImportController=graphDbImportController,
                                        readApi=self._readApi,
                                        dbSessionCreator=dbSessionCreator,
                                        dbEngine=dbEngine)

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
