import logging
from datetime import datetime
from typing import List

from twisted.internet.defer import Deferred, inlineCallbacks

from peek_plugin_graphdb._private.server.GraphDBReadApi import GraphDBReadApi
from peek_plugin_graphdb._private.worker.tasks.GraphDbItemImportTask import \
    importGraphSegment
from peek_plugin_graphdb.tuples.ImportGraphDbItemTuple import ImportGraphDbItemTuple
from vortex.Payload import Payload

from peek_plugin_graphdb.tuples.GraphDbImportEdgeTuple import GraphDbImportEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbImportVertexTuple import GraphDbImportVertexTuple

logger = logging.getLogger(__name__)


class GraphDbImportController:
    """ GraphDB Import Controller
    """

    def __init__(self, dbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    def setReadApi(self, readApi:GraphDBReadApi):
        self._readApi = readApi

    def shutdown(self):
        self._readApi = None

    @inlineCallbacks
    def importGraphSegment(self, modelSetName: str, segmentHash: str,
                           vertices: List[GraphDbImportVertexTuple],
                           edges: List[GraphDbImportEdgeTuple]) -> Deferred:
        """ Import Graph Segment

        1) set the  coordSetId

        2) Drop all disps with matching importGroupHash

        :param modelSetName:  The name of the model set for the live db.
        :param segmentHash: The unique segment hash for the graph segment being imported.
        :param vertices: A list of vertices to import / update.
        :param edges: A list of edges to import / update.

        :return: A deferred that fires when the update is complete.
        :rtype: None
        :return:
        """

        newKeys = yield importGraphSegment.delay(
            modelSetName=modelSetName,
            newItems=newItems
        )

        newTuples = []

        deferredGenerator = self._readApi.bulkLoadDeferredGenerator(
            modelSetName, keyList=newKeys)
        while True:
            d = next(deferredGenerator)
            newTuplesChunk = yield d  # List[GraphDbDisplayValueTuple]
            newTuples += newTuplesChunk

            # The end of the list is marked my an empty result
            if not newTuplesChunk:
                break

        # If there are no tuples, do nothing
        if not newTuples:
            return

        # Notify the agent of the new keys.
        self._readApi.edgeAdditionObservable(modelSetName).on_next(newTuples)