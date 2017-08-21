from typing import List

from abc import ABCMeta, abstractmethod
from twisted.internet.defer import Deferred

from peek_plugin_graphdb.tuples.ImportGraphDbItemTuple import ImportGraphDbItemTuple
from peek_plugin_graphdb.tuples.GraphDbDisplayValueUpdateTuple import \
    GraphDbDisplayValueUpdateTuple
from peek_plugin_graphdb.tuples.GraphDbRawValueUpdateTuple import GraphDbRawValueUpdateTuple


class GraphDBWriteApiABC(metaclass=ABCMeta):
    @abstractmethod
    def updateRawValues(self, modelSetName: str,
                        updates: List[GraphDbRawValueUpdateTuple]) -> Deferred:
        """ Process Live DB Raw Value Updates

        Tells the live db that values have updated in the field, or wherever.

        :param modelSetName:  The name of the model set for the live db
        :param updates: A list of tuples containing the value updates

        :return: A deferred that fires when the update is complete.
        :rtype: bool

        """

    @abstractmethod
    def updateDisplayValue(self, modelSetName: str,
                           updates: List[GraphDbDisplayValueUpdateTuple]) -> Deferred:
        """ Process Live DB Raw+Display Value Updates

        Tells the live db that values have updated in the field, or wherever.

        :param modelSetName:  The name of the model set for the live db
        :param updates: A list of tuples containing the value updates

        :return: A deferred that fires when the update is complete.
        :rtype: bool

        """

    @abstractmethod
    def importGraphDbItems(self, modelSetName: str,
                          newItems: List[ImportGraphDbItemTuple]) -> Deferred:
        """ Import GraphDB Items

        Create new Live DB Items with Raw + Display values

        If an item already exists, it's value is update.

        :param modelSetName:  The name of the model set for the live db
        :param newItems: A list of tuples containing the value updates

        :return: A deferred that fires when the inserts are complete.
        :rtype: bool

        """

    @abstractmethod
    def prioritiseGraphDbValueAcquisition(self, modelSetName: str,
                                         graphDbKeys: List[str]) -> Deferred:
        """ Prioritise GraphDB Value Aquasitions

        When this method was first created, it was used for the diagram to tell the
        RealTime agent which keys to update as they were viewed by the user.

        :param modelSetName:  The name of the model set for the live db
        :param graphDbKeys: A list of the graphdb keys to watch

        :return: A deferred that fires when the inserts are complete.
        :rtype: bool

        """
