from abc import ABCMeta, abstractmethod

from peek_plugin_graphdb.server.GraphDbReadApiABC import GraphDbReadApiABC
from peek_plugin_graphdb.server.GraphDbWriteApiABC import GraphDbWriteApiABC


class GraphDbApiABC(metaclass=ABCMeta):
    @property
    @abstractmethod
    def writeApi(self) -> GraphDbWriteApiABC:
        """ GraphDb Write API

        This API is for all the methods that make changes to the GraphDb

        :return: A reference to the GraphDbWriteApiABC instance

        """

    @property
    @abstractmethod
    def readApi(self) -> GraphDbReadApiABC:
        """ GraphDb Read API

        This API is for all the methods to read changes from the GraphDb

        :return: A reference to the GraphDbReadApiABC instance

        """
