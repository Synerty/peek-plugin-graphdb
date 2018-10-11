import logging
from collections import defaultdict
from typing import Dict, List, Set

from twisted.internet.defer import inlineCallbacks
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.PayloadFilterKeys import plDeleteKey
from vortex.TupleSelector import TupleSelector

from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.server.client_handlers.ClientTraceConfigLoadRpc import \
    ClientTraceConfigLoadRpc
from peek_plugin_graphdb.tuples.GraphDbTraceConfigTuple import \
    GraphDbTraceConfigTuple

logger = logging.getLogger(__name__)

clientTraceConfigUpdateFromServerFilt = dict(key="clientTraceConfigUpdateFromServer")
clientTraceConfigUpdateFromServerFilt.update(graphDbFilt)


class TraceConfigCacheController:
    """ TraceConfig Cache Controller

    The TraceConfig cache controller stores all the chunks in memory,
    allowing fast access from the mobile and desktop devices.

    """

    LOAD_CHUNK = 32

    def __init__(self, clientId: str):
        self._clientId = clientId
        self._tupleObservable = None

        #: This stores the cache of segment data for the clients
        self._cache: Dict[str, Dict[str, GraphDbTraceConfigTuple]] = defaultdict(dict)

        self._endpoint = PayloadEndpoint(clientTraceConfigUpdateFromServerFilt,
                                         self._processTraceConfigPayload)

    def setTupleObservable(self, tupleObservable):
        self._tupleObservable = tupleObservable

    @inlineCallbacks
    def start(self):
        yield self.reloadCache()

    def shutdown(self):
        self._tupleObservable = None

        self._endpoint.shutdown()
        self._endpoint = None

        self._cache = defaultdict(dict)

    @inlineCallbacks
    def reloadCache(self):
        self._cache = defaultdict(dict)

        offset = 0
        while True:
            logger.info(
                "Loading TraceConfig %s to %s" % (offset, offset + self.LOAD_CHUNK)
            )
            traceConfigTuples: List[GraphDbTraceConfigTuple] = (
                yield ClientTraceConfigLoadRpc.loadTraceConfigs(offset, self.LOAD_CHUNK)
            )

            if not traceConfigTuples:
                break

            self._loadTraceConfigIntoCache(traceConfigTuples)

            offset += self.LOAD_CHUNK

    @inlineCallbacks
    def _processTraceConfigPayload(self, payloadEnvelope: PayloadEnvelope, **kwargs):
        payload = yield payloadEnvelope.decodePayloadDefer()

        if payload.filt.get(plDeleteKey):
            modelSetKey = payload.tuples["modelSetKey"]
            traceConfigKeys = payload.tuples["traceConfigKeys"]
            self._removeTraceConfigFromCache(modelSetKey, traceConfigKeys)
            return

        modelSetKey = payload.tuples["modelSetKey"]
        importGroupHash = payload.tuples["importGroupHash"]

        segmentTuples: List[GraphDbTraceConfigTuple] = payload.tuples["tuples"]
        self._loadTraceConfigIntoCache(segmentTuples, modelSetKey, set(importGroupHash))

    def _removeTraceConfigFromCache(self, modelSetKey: str, traceConfigKeys: List[str]):
        subCache = self._cache[modelSetKey]

        logger.debug("Received TraceConfig deletes from server, %s %s removed",
                     modelSetKey, len(traceConfigKeys))

        for traceConfigKey in traceConfigKeys:
            if traceConfigKey in subCache:
                subCache.pop(traceConfigKey)

        self._tupleObservable.no(TupleSelector(GraphDbTraceConfigTuple.tupleType(),
                                               dict(modelSetKey=modelSetKey)))

    def _loadTraceConfigIntoCache(self, traceConfigTuples: List[GraphDbTraceConfigTuple],
                                  modelSetKey: str, importGroupHash: Set[str]):
        subCache = self._cache[modelSetKey]

        traceKeysUpdated: Set[str] = {
            traceConfig.key for traceConfig in traceConfigTuples
        }

        traceKeysRemoved: Set[str] = {
            tc.key
            for tc in subCache.values()
            if tc.importGroupHash in importGroupHash
        }

        traceKeysRemoved -= traceKeysUpdated

        for traceConfig in traceConfigTuples:
            subCache[traceConfig.key] = traceConfig

        for traceConfigKey in traceKeysRemoved:
            if traceConfigKey in subCache:
                subCache.pop(traceConfigKey)

        logger.debug("Received TraceConfig updates from server,"
                     "%s %s removed, %s added/updated",
                     modelSetKey, len(traceKeysRemoved), len(traceKeysUpdated))

        self._tupleObservable.no(TupleSelector(GraphDbTraceConfigTuple.tupleType(),
                                               dict(modelSetKey=modelSetKey)))

    def traceConfigTuple(self, modelSetKey: str,
                         traceConfigKey: str) -> GraphDbTraceConfigTuple:
        return self._cache[modelSetKey][traceConfigKey]

    def traceConfigTuples(self, modelSetKey: str) -> List[GraphDbTraceConfigTuple]:
        return list(self._cache[modelSetKey].values())
