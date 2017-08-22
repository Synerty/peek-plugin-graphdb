import logging

from collections import defaultdict
from rx.subjects import Subject

from peek_plugin_graphdb._private.server.controller.GraphDbModelController import \
    GraphDbModelController
from peek_plugin_graphdb.server.GraphDBReadApiABC import GraphDBReadApiABC

logger = logging.getLogger(__name__)


class GraphDBReadApi(GraphDBReadApiABC):
    def __init__(self, graphDbController: GraphDbModelController):
        self._graphDbController = graphDbController

        self._propUpdateSubject = defaultdict(Subject)
        self._edgeAdditionSubject = defaultdict(Subject)
        self._edgeDeletionSubject = defaultdict(Subject)
        self._vertexAdditionSubject = defaultdict(Subject)
        self._vertexDeletionSubject = defaultdict(Subject)

    def shutdown(self):
        pass

    def propUpdateObservable(self, modelSetName: str) -> Subject:
        return self._propUpdateSubject[modelSetName]

    def edgeAdditionObservable(self, modelSetName: str) -> Subject:
        return self._edgeAdditionSubject[modelSetName]

    def edgeDeletionObservable(self, modelSetName: str) -> Subject:
        return self._edgeDeletionSubject[modelSetName]

    def vertexAdditionObservable(self, modelSetName: str) -> Subject:
        return self._vertexAdditionSubject[modelSetName]

    def vertexDeletionObservable(self, modelSetName: str) -> Subject:
        return self._vertexDeletionSubject[modelSetName]
