import logging
from datetime import datetime
from typing import List

from sqlalchemy import bindparam
from sqlalchemy.sql.expression import and_
from twisted.internet import defer
from twisted.internet.defer import Deferred, inlineCallbacks

from peek_plugin_graphdb._private.server.GraphDBReadApi import GraphDBReadApi
from peek_plugin_graphdb._private.server.controller.GraphDbModelController import \
    GraphDbModelController
from peek_plugin_graphdb._private.server.controller.GraphDbImportController import \
    GraphDbImportController
from peek_plugin_graphdb._private.storage.GraphDbVertex import GraphDbItem
from peek_plugin_graphdb._private.storage.GraphDbModelSet import getOrCreateGraphDbModelSet
from peek_plugin_graphdb._private.worker.tasks.GraphDbItemUpdateTask import updateValues
from peek_plugin_graphdb.server.GraphDBWriteApiABC import GraphDBWriteApiABC
from peek_plugin_graphdb.tuples.ImportGraphDbItemTuple import ImportGraphDbItemTuple
from peek_plugin_graphdb.tuples.GraphDbDisplayValueUpdateTuple import \
    GraphDbDisplayValueUpdateTuple
from peek_plugin_graphdb.tuples.GraphDbRawValueUpdateTuple import GraphDbRawValueUpdateTuple
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload

from peek_plugin_graphdb.tuples.GraphDbImportEdgeTuple import GraphDbImportEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbImportVertexTuple import GraphDbImportVertexTuple

logger = logging.getLogger(__name__)


class GraphDBWriteApi(GraphDBWriteApiABC):
    def __init__(self, graphDbController: GraphDbModelController,
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

    def importGraphSegment(self, modelSetName: str, segmentHash: str,
                           vertices: List[GraphDbImportVertexTuple],
                           edges: List[GraphDbImportEdgeTuple]) -> Deferred:
        if not vertices and not edges:
            return defer.succeed(True)

        return self._graphDbImportController.importGraphSegment(
            modelSetName=modelSetName,
            segmentHash=segmentHash,
            vertices=vertices,
            edges=edges
        )
