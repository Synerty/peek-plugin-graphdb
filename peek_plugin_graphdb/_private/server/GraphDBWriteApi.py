import logging
from datetime import datetime
from typing import List

from sqlalchemy import bindparam
from sqlalchemy.sql.expression import and_
from twisted.internet import defer
from twisted.internet.defer import Deferred, inlineCallbacks

from peek_plugin_graphdb._private.server.GraphDBReadApi import GraphDBReadApi
from peek_plugin_graphdb._private.server.controller.GraphDbController import \
    GraphDbController
from peek_plugin_graphdb._private.server.controller.GraphDbImportController import \
    GraphDbImportController
from peek_plugin_graphdb._private.storage.GraphDbItem import GraphDbItem
from peek_plugin_graphdb._private.storage.GraphDbModelSet import getOrCreateGraphDbModelSet
from peek_plugin_graphdb._private.worker.tasks.GraphDbItemUpdateTask import updateValues
from peek_plugin_graphdb.server.GraphDBWriteApiABC import GraphDBWriteApiABC
from peek_plugin_graphdb.tuples.ImportGraphDbItemTuple import ImportGraphDbItemTuple
from peek_plugin_graphdb.tuples.GraphDbDisplayValueUpdateTuple import \
    GraphDbDisplayValueUpdateTuple
from peek_plugin_graphdb.tuples.GraphDbRawValueUpdateTuple import GraphDbRawValueUpdateTuple
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload

logger = logging.getLogger(__name__)


class GraphDBWriteApi(GraphDBWriteApiABC):
    def __init__(self, graphDbController: GraphDbController,
                 graphDbImportController: GraphDbImportController,
                 readApi: GraphDBReadApi,
                 dbSessionCreator,
                 dbEngine):
        self._graphDbController = graphDbController
        self._graphDbImportController = graphDbImportController
        self._readApi = readApi
        self._dbSessionCreator = dbSessionCreator
        self._dbEngine = dbEngine

    def shutdown(self):
        pass

    @inlineCallbacks
    def updateRawValues(self, modelSetName: str,
                        updates: List[GraphDbRawValueUpdateTuple]) -> Deferred:
        """ Update Raw Values

        """
        if not updates:
            return

        yield updateValues.delay(modelSetName, updates, raw=True)
        self._readApi.rawValueUpdatesObservable(modelSetName).on_next(updates)

    @inlineCallbacks
    def updateDisplayValue(self, modelSetName: str,
                           updates: List[GraphDbDisplayValueUpdateTuple]) -> Deferred:
        """ Update Display Values

        """
        if not updates:
            return

        yield updateValues.delay(modelSetName, updates, raw=False)
        self._readApi.displayValueUpdatesObservable(modelSetName).on_next(updates)

    def importGraphDbItems(self, modelSetName: str,
                          newItems: List[ImportGraphDbItemTuple]) -> Deferred:
        if not newItems:
            return defer.succeed(True)

        return self._graphDbImportController.importGraphDbItems(modelSetName, newItems)

    def prioritiseGraphDbValueAcquisition(self, modelSetName: str,
                                         graphDbKeys: List[str]) -> Deferred:
        self._readApi.priorityGraphDbKeysObservable(modelSetName).on_next(graphDbKeys)
        return defer.succeed(True)

