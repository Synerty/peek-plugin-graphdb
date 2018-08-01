import logging

from collections import defaultdict
from rx.subjects import Subject

from peek_plugin_graphdb._private.server.controller.MainController import MainController
from peek_plugin_graphdb.server.GraphDbReadApiABC import GraphDbReadApiABC

logger = logging.getLogger(__name__)


class GraphDbReadApi(GraphDbReadApiABC):
    def __init__(self, mainController: MainController):
        self._mainController = mainController

        self._vertexAdditionSubject = defaultdict(Subject)
        self._vertexDeletionSubject = defaultdict(Subject)
        self._vertexAttrUpdateSubject = defaultdict(Subject)
        self._vertexPropUpdateSubject = defaultdict(Subject)

        self._edgeAdditionSubject = defaultdict(Subject)
        self._edgeDeletionSubject = defaultdict(Subject)
        self._edgePropUpdateSubject = defaultdict(Subject)

    def shutdown(self):
        pass

    # ---------------
    # Vertex observables

    def vertexAdditionObservable(self, modelSetKey: str) -> Subject:
        return self._vertexAdditionSubject[modelSetKey]

    def vertexDeletionObservable(self, modelSetKey: str) -> Subject:
        return self._vertexDeletionSubject[modelSetKey]

    def vertexAttrUpdateObservable(self, modelSetKey: str) -> Subject:
        return self._vertexAttrUpdateSubject[modelSetKey]

    def vertexPropUpdateObservable(self, modelSetKey: str) -> Subject:
        return self._vertexPropUpdateSubject[modelSetKey]

    # ---------------
    # Edge observables

    def edgeAdditionObservable(self, modelSetKey: str) -> Subject:
        return self._edgeAdditionSubject[modelSetKey]

    def edgeDeletionObservable(self, modelSetKey: str) -> Subject:
        return self._edgeDeletionSubject[modelSetKey]

    def edgePropUpdateObservable(self, modelSetKey: str) -> Subject:
        return self._edgePropUpdateSubject[modelSetKey]
