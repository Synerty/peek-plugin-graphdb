import logging

from collections import defaultdict
from rx.subjects import Subject

from peek_plugin_graphdb._private.server.controller.MainController import MainController
from peek_plugin_graphdb.server.GraphDBReadApiABC import GraphDBReadApiABC

logger = logging.getLogger(__name__)


class GraphDBReadApi(GraphDBReadApiABC):
    def __init__(self, mainController: MainController):
        self._mainController = mainController

        self._propUpdateSubject = defaultdict(Subject)
        self._edgeAdditionSubject = defaultdict(Subject)
        self._edgeDeletionSubject = defaultdict(Subject)
        self._vertexAdditionSubject = defaultdict(Subject)
        self._vertexDeletionSubject = defaultdict(Subject)

    def shutdown(self):
        pass

    def propUpdateObservable(self, modelSetKey: str) -> Subject:
        return self._propUpdateSubject[modelSetKey]

    def edgeAdditionObservable(self, modelSetKey: str) -> Subject:
        return self._edgeAdditionSubject[modelSetKey]

    def edgeDeletionObservable(self, modelSetKey: str) -> Subject:
        return self._edgeDeletionSubject[modelSetKey]

    def vertexAdditionObservable(self, modelSetKey: str) -> Subject:
        return self._vertexAdditionSubject[modelSetKey]

    def vertexDeletionObservable(self, modelSetKey: str) -> Subject:
        return self._vertexDeletionSubject[modelSetKey]
