from peek_plugin_graphdb._private.server.LiveDBReadApi import LiveDBReadApi
from peek_plugin_graphdb._private.server.LiveDBWriteApi import LiveDBWriteApi
from peek_plugin_graphdb._private.server.controller.LiveDbController import \
    LiveDbController
from peek_plugin_graphdb._private.server.controller.LiveDbImportController import \
    LiveDbImportController
from peek_plugin_graphdb.server.LiveDBApiABC import LiveDBApiABC
from peek_plugin_graphdb.server.LiveDBReadApiABC import LiveDBReadApiABC
from peek_plugin_graphdb.server.LiveDBWriteApiABC import LiveDBWriteApiABC


class LiveDBApi(LiveDBApiABC):
    def __init__(self, liveDbController: LiveDbController,
                 liveDbImportController: LiveDbImportController,
                 dbSessionCreator,
                 dbEngine):
        self._readApi = LiveDBReadApi(liveDbController=liveDbController,
                                      dbSessionCreator=dbSessionCreator,
                                      dbEngine=dbEngine)
        self._writeApi = LiveDBWriteApi(liveDbController=liveDbController,
                                        liveDbImportController=liveDbImportController,
                                        readApi=self._readApi,
                                        dbSessionCreator=dbSessionCreator,
                                        dbEngine=dbEngine)

    def shutdown(self):
        self._readApi.shutdown()
        self._writeApi.shutdown()

        self._readApi = None
        self._writeApi = None

    @property
    def writeApi(self) -> LiveDBWriteApiABC:
        return self._writeApi

    @property
    def readApi(self) -> LiveDBReadApiABC:
        return self._readApi
