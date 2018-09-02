import logging

from twisted.internet import defer
from twisted.internet.defer import inlineCallbacks

from peek_plugin_graphdb._private.worker.tasks.ImportTask import createOrUpdateSegments

logger = logging.getLogger(__name__)


class ImportController:
    def __init__(self):
        pass

    def shutdown(self):
        pass

    @inlineCallbacks
    def createOrUpdateSegments(self, modelSetKey: str, graphSegmentEncodedPayload: bytes):
        yield createOrUpdateSegments.delay(modelSetKey, graphSegmentEncodedPayload)

    def deleteSegment(self, modelSetKey: str, segmentKey: str):
        return defer.succeed(None)
