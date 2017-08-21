from typing import List

from abc import ABCMeta, abstractmethod
from twisted.internet.defer import Deferred

from peek_plugin_graphdb.tuples.ImportLiveDbItemTuple import ImportLiveDbItemTuple
from peek_plugin_graphdb.tuples.LiveDbDisplayValueUpdateTuple import \
    LiveDbDisplayValueUpdateTuple
from peek_plugin_graphdb.tuples.LiveDbRawValueUpdateTuple import LiveDbRawValueUpdateTuple


class LiveDBWriteApiABC(metaclass=ABCMeta):
    @abstractmethod
    def updateRawValues(self, modelSetName: str,
                        updates: List[LiveDbRawValueUpdateTuple]) -> Deferred:
        """ Process Live DB Raw Value Updates

        Tells the live db that values have updated in the field, or wherever.

        :param modelSetName:  The name of the model set for the live db
        :param updates: A list of tuples containing the value updates

        :return: A deferred that fires when the update is complete.
        :rtype: bool

        """

    @abstractmethod
    def updateDisplayValue(self, modelSetName: str,
                           updates: List[LiveDbDisplayValueUpdateTuple]) -> Deferred:
        """ Process Live DB Raw+Display Value Updates

        Tells the live db that values have updated in the field, or wherever.

        :param modelSetName:  The name of the model set for the live db
        :param updates: A list of tuples containing the value updates

        :return: A deferred that fires when the update is complete.
        :rtype: bool

        """

    @abstractmethod
    def importLiveDbItems(self, modelSetName: str,
                          newItems: List[ImportLiveDbItemTuple]) -> Deferred:
        """ Import LiveDB Items

        Create new Live DB Items with Raw + Display values

        If an item already exists, it's value is update.

        :param modelSetName:  The name of the model set for the live db
        :param newItems: A list of tuples containing the value updates

        :return: A deferred that fires when the inserts are complete.
        :rtype: bool

        """

    @abstractmethod
    def prioritiseLiveDbValueAcquisition(self, modelSetName: str,
                                         liveDbKeys: List[str]) -> Deferred:
        """ Prioritise LiveDB Value Aquasitions

        When this method was first created, it was used for the diagram to tell the
        RealTime agent which keys to update as they were viewed by the user.

        :param modelSetName:  The name of the model set for the live db
        :param liveDbKeys: A list of the graphdb keys to watch

        :return: A deferred that fires when the inserts are complete.
        :rtype: bool

        """
