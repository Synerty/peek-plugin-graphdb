import logging
from typing import List

from twisted.internet.defer import inlineCallbacks, Deferred

from peek_plugin_graphdb._private.server.client_handlers.ClientTraceConfigUpdateHandler import \
    ClientTraceConfigUpdateHandler
from peek_plugin_graphdb._private.worker.tasks import ImportGraphSegmentTask
from peek_plugin_graphdb._private.worker.tasks import ImportTraceConfigTask

logger = logging.getLogger(__name__)


class ImportController:
    def __init__(self, traceConfigUpdateHandler: ClientTraceConfigUpdateHandler):
        self._traceConfigUpdateHandler = traceConfigUpdateHandler

    def shutdown(self):
        pass

    @inlineCallbacks
    def createOrUpdateSegments(self, graphSegmentEncodedPayload: bytes):
        yield ImportGraphSegmentTask.createOrUpdateSegments.delay(
            graphSegmentEncodedPayload
        )

    @inlineCallbacks
    def deleteSegment(self, modelSetKey: str, segmentKeys: List[str]):
        yield ImportGraphSegmentTask.deleteSegment.delay(modelSetKey, segmentKeys)

    @inlineCallbacks
    def createOrUpdateTraceConfig(self, traceEncodedPayload: bytes) -> Deferred:
        insertedOrCreated = yield ImportTraceConfigTask.createOrUpdateTraceConfigs.delay(
            traceEncodedPayload
        )

        for modelSetKey, traceConfigKeys in insertedOrCreated.items():
            self._traceConfigUpdateHandler.sendCreatedOrUpdatedUpdates(
                modelSetKey, traceConfigKeys
            )

    @inlineCallbacks
    def deleteTraceConfig(self, modelSetKey: str, traceConfigKeys: List[str]) -> Deferred:
        yield ImportTraceConfigTask.deleteTraceConfig.delay(
            modelSetKey, traceConfigKeys
        )

        self._traceConfigUpdateHandler.sendDeleted(
            modelSetKey, traceConfigKeys
        )
