from abc import ABCMeta, abstractmethod

from peek_plugin_graphdb.server.GraphDBReadApiABC import GraphDBReadApiABC
from peek_plugin_graphdb.server.GraphDBWriteApiABC import GraphDBWriteApiABC


class GraphDBApiABC(metaclass=ABCMeta):
    @property
    @abstractmethod
    def writeApi(self) -> GraphDBWriteApiABC:
        """ GraphDB Write API

        This API is for all the methods that make changes to the GraphDB

        :return: A reference to the GraphDBWriteApiABC instance

        """

    @property
    @abstractmethod
    def readApi(self) -> GraphDBReadApiABC:
        """ GraphDB Read API

        This API is for all the methods to read changes from the GraphDB

        :return: A reference to the GraphDBReadApiABC instance

        """
