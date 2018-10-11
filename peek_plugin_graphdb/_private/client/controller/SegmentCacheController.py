import logging
from collections import defaultdict
from typing import Dict, List

from twisted.internet.defer import inlineCallbacks

from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.server.client_handlers.ClientSegmentChunkLoadRpc import \
    ClientSegmentChunkLoadRpc
from peek_plugin_graphdb._private.storage.GraphDbEncodedChunk import \
    GraphDbEncodedChunk
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope

logger = logging.getLogger(__name__)

clientSegmentUpdateFromServerFilt = dict(key="clientSegmentUpdateFromServer")
clientSegmentUpdateFromServerFilt.update(graphDbFilt)


class SegmentCacheController:
    """ Segment Cache Controller

    The Segment cache controller stores all the chunks in memory,
    allowing fast access from the mobile and desktop devices.

    """

    LOAD_CHUNK = 32

    def __init__(self, clientId: str):
        self._clientId = clientId
        self._webAppHandler = None

        #: This stores the cache of segment data for the clients
        self._cache: Dict[int, GraphDbEncodedChunk] = {}

        self._endpoint = PayloadEndpoint(clientSegmentUpdateFromServerFilt,
                                         self._processSegmentPayload)

    def setSegmentCacheHandler(self, handler):
        self._webAppHandler = handler

    @inlineCallbacks
    def start(self):
        yield self.reloadCache()

    def shutdown(self):
        self._tupleObservable = None

        self._endpoint.shutdown()
        self._endpoint = None

        self._cache = {}

    @inlineCallbacks
    def reloadCache(self):
        self._cache = {}

        offset = 0
        while True:
            logger.info(
                "Loading SegmentChunk %s to %s" % (offset, offset + self.LOAD_CHUNK))
            encodedChunkTuples: List[GraphDbEncodedChunk] = (
                yield ClientSegmentChunkLoadRpc.loadSegmentChunks(offset, self.LOAD_CHUNK)
            )

            if not encodedChunkTuples:
                break

            self._loadSegmentIntoCache(encodedChunkTuples)

            offset += self.LOAD_CHUNK

    @inlineCallbacks
    def _processSegmentPayload(self, payloadEnvelope: PayloadEnvelope, **kwargs):
        paylod = yield payloadEnvelope.decodePayloadDefer()
        segmentTuples: List[GraphDbEncodedChunk] = paylod.tuples
        self._loadSegmentIntoCache(segmentTuples)

    def _loadSegmentIntoCache(self,
                                  encodedChunkTuples: List[GraphDbEncodedChunk]):
        chunkKeysUpdated: List[str] = []

        for t in encodedChunkTuples:

            if (not t.chunkKey in self._cache or
                    self._cache[t.chunkKey].lastUpdate != t.lastUpdate):
                self._cache[t.chunkKey] = t
                chunkKeysUpdated.append(t.chunkKey)

        logger.debug("Received segment updates from server, %s", chunkKeysUpdated)

        self._webAppHandler.notifyOfSegmentUpdate(chunkKeysUpdated)

    def segmentChunk(self, chunkKey) -> GraphDbEncodedChunk:
        return self._cache.get(chunkKey)

    def segmentKeys(self) -> List[int]:
        return list(self._cache)
