from abc import ABCMeta, abstractmethod
from rx.subjects import Subject


class GraphDbReadApiABC(metaclass=ABCMeta):
    # ---------------
    # Vertex Methods

    @abstractmethod
    def vertexAdditionObservable(self, modelSetKey: str) -> Subject:
        """ Vertex Addition Observable

        :param modelSetKey:  The name of the model set to observe

        :return: An observable that emits a GraphDbVertexTuple.

        """

    @abstractmethod
    def vertexDeletionObservable(self, modelSetKey: str) -> Subject:
        """ Vertex Deletion Observable

        :param modelSetKey:  The name of the model set to observe

        :return: An observable that emits a GraphDbVertexTuple.

        """

    @abstractmethod
    def vertexAttrUpdateObservable(self, modelSetKey: str) -> Subject:
        """ Vertex Attribute Update Observable

        :param modelSetKey:  The name of the model set to observe

        :return: An observable that emits a GraphDbVertexTuple.

        """

    @abstractmethod
    def vertexPropUpdateObservable(self, modelSetKey: str) -> Subject:
        """ Vertex Property Update Observable

        :param modelSetKey:  The name of the model set to observe

        :return: An observable that emits a GraphDbVertexTuple.

        """

    # ---------------
    # Edge Methods


    @abstractmethod
    def edgeAdditionObservable(self, modelSetKey: str) -> Subject:
        """ Edge Addition Observable

        :param modelSetKey:  The name of the model set to observe

        :return: An observable that emits a GraphDbEdgeTuple.

        """

    @abstractmethod
    def edgeDeletionObservable(self, modelSetKey: str) -> Subject:
        """ Edge Deletion Observable

        :param modelSetKey:  The name of the model set to observe

        :return: An observable that emits a GraphDbEdgeTuple.

        """

    @abstractmethod
    def edgePropUpdateObservable(self, modelSetKey: str) -> Subject:
        """ Edge Property Update Observable

        :param modelSetKey:  The name of the model set to observe

        :return: An observable that emits a GraphDbEdgeTuple.

        """
