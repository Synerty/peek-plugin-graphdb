from abc import ABCMeta, abstractmethod

from twisted.internet.defer import Deferred

from peek_plugin_graphdb.tuples.GraphDbImportSegmentTuple import GraphDbImportSegmentTuple


class GraphDbApiABC(metaclass=ABCMeta):

    @abstractmethod
    def createOrUpdateSegment(self, modelSetKey: str,
                              graphSegmentEncodedPayload: bytes) -> Deferred:
        """ Create or Update Segment

        Add new documents to the document db

        :param modelSetKey: An encoded payload containing :code:`GraphDbImportSegmentTuple`
        :param graphSegmentEncodedPayload: An encoded payload containing :code:`GraphDbImportSegmentTuple`
        :return: A deferred that fires when the creates or updates are complete

        """

    @abstractmethod
    def deleteSegment(self, modelSetKey: str, segmentKey: str) -> Deferred:
        """ Delete Segment

        Delete documents from the document db.

        :param modelSetKey: The model set key to delete documents from
        :param segmentKey: The key of the segment to delete
        :return: A deferred that fires when the delete is complete

        """
