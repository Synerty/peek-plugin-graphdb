import logging
from typing import List, Optional

from twisted.internet.defer import Deferred, inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.TupleAction import TupleActionABC
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_graphdb._private.server.GraphDBReadApi import GraphDBReadApi
from peek_plugin_graphdb._private.server.graph.GraphModel import \
    GraphModel
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet, \
    getOrCreateGraphDbModelSet

logger = logging.getLogger(__name__)


class MainController(TupleActionProcessorDelegateABC):
    def __init__(self, dbSessionCreator, tupleObservable: TupleDataObservableHandler):
        self._dbSessionCreator = dbSessionCreator
        self._tupleObservable = tupleObservable
        self._readApi = None

        self._graphsByModelSetKey = {}

    @inlineCallbacks
    def start(self, readApi: GraphDBReadApi) -> Deferred:
        self._readApi = readApi

        modelSets = yield self._loadModelSets()

        for modelSet in modelSets:
            graph = GraphModel(self._dbSessionCreator, self._readApi, modelSet)
            self._graphsByModelSetKey[modelSet.key] = graph
            yield graph.start()

    def shutdown(self):
        for graph in self._graphsByModelSetKey.values():
            graph.shutdown()

        del self._graphsByModelSetKey

    def processTupleAction(self, tupleAction: TupleActionABC) -> Deferred:
        raise NotImplementedError(tupleAction.tupleName())

    @inlineCallbacks
    def graphForModelSetKey(self, modelSetKey: str) -> Deferred:
        graphModel =  self._graphsByModelSetKey.get(modelSetKey)
        if  graphModel:
            return graphModel

        modelSet = yield self._createModelSet(modelSetKey)
        graphModel = GraphModel(self._dbSessionCreator, self._readApi, modelSet)
        yield graphModel.start()
        self._graphsByModelSetKey[modelSetKey] = graphModel
        return graphModel


    @deferToThreadWrapWithLogger(logger)
    def _createModelSet(self, modelSetKey) -> GraphDbModelSet:
        ormSession = self._dbSessionCreator()
        try:
            modelSet =  getOrCreateGraphDbModelSet(ormSession, modelSetKey)
            ormSession.expunge_all()
            return modelSet

        finally:
            ormSession.close()

    @deferToThreadWrapWithLogger(logger)
    def _loadModelSets(self) -> List[GraphDbModelSet]:
        ormSession = self._dbSessionCreator()
        try:
            all = ormSession.query(GraphDbModelSet).all()
            ormSession.expunge_all()
            return all

        finally:
            ormSession.close()
