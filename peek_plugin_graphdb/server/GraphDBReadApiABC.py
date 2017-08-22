from typing import Optional, List

from abc import ABCMeta, abstractmethod
from rx.subjects import Subject
from twisted.internet.defer import Deferred


class GraphDBReadApiABC(metaclass=ABCMeta):
    @abstractmethod
    def propUpdateObservable(self, modelSetKey: str) -> Subject:
        """ Priority Live DB ID Observable

        This observable emits list of keys that the live db acquisition plugins should
        prioritise.

        This list will represent keys relating to the objects that are
        currently being viewed.

        :param modelSetKey:  The name of the model set to import the disps into

        :return: An observable that emits a List[str].

        """

    @abstractmethod
    def edgeAdditionObservable(self, modelSetKey: str) -> Subject:
        """ Live DB Tuple Added Items Observable

        Return an observable that fires when graphdb items are added

        :param modelSetKey: The name of the model set for the live db

        :return: An observable that fires when keys are removed from the live db
        :rtype: An observable that emits List[GraphDbDisplayValueTuple]

        """

    @abstractmethod
    def edgeDeletionObservable(self, modelSetKey: str) -> Subject:
        """ Live DB Tuple Removed Items Observable

        Return an observable that fires when graphdb items are removed

        :param modelSetKey:  The name of the model set for the live db

        :return: An observable that fires when keys are removed from the live db
        :rtype: An observable that emits List[str]

        """


    @abstractmethod
    def vertexAdditionObservable(self, modelSetKey: str) -> Subject:
        """ Raw Value Update Observable

        Return an observable that fires with lists of C{GraphDbRawValueTuple} tuples
        containing updates to live db values.

        :param modelSetKey:  The name of the model set for the live db

        :return: An observable that fires when values are updated in the graphdb
        :rtype: Subject[List[GraphDbRawValueTuple]]

        """

    @abstractmethod
    def vertexDeletionObservable(self, modelSetKey: str) -> Subject:
        """ Display Value Update Observable

        Return an observable that fires with lists of C{GraphDbDisplayValueTuple} tuples
        containing updates to live db values.

        :param modelSetKey:  The name of the model set for the live db

        :return: An observable that fires when values are updated in the graphdb
        :rtype: An observable that fires with List[GraphDbDisplayValueTuple]

        """
