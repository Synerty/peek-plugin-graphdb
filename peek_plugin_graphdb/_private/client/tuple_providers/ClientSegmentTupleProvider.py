import json
import logging
from collections import defaultdict
from typing import Union, List

from twisted.internet.defer import Deferred

from peek_plugin_graphdb._private.client.controller.SegmentCacheController import \
    SegmentCacheController
from peek_plugin_graphdb._private.storage.GraphDbEncodedChunk import GraphDbEncodedChunk
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from peek_plugin_graphdb._private.worker.tasks._CalcChunkKey import makeChunkKey
from peek_plugin_graphdb.tuples.GraphDbSegmentTuple import GraphDbSegmentTuple
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class ClientSegmentTupleProvider(TuplesProviderABC):
    def __init__(self, cacheHandler: SegmentCacheController):
        self._cacheHandler = cacheHandler

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        raise NotImplementedError("Server querying not implemented")

        '''
        modelSetKey = tupleSelector.selector["modelSetKey"]
        keys = tupleSelector.selector["keys"]

        keysByChunkKey = defaultdict(list)

        foundSegments: List[GraphDbSegmentTuple] = []

        for key in keys:
            keysByChunkKey[makeChunkKey(modelSetKey, key)].append(key)

        for chunkKey, subKeys in keysByChunkKey.items():
            chunk: GraphDbEncodedChunk = self._cacheHandler.segmentChunk(chunkKey)

            if not chunk:
                logger.warning("Segment chunk %s is missing from cache", chunkKey)
                continue

            docsByKeyStr = Payload().fromEncodedPayload(chunk.encodedData).tuples[0]
            docsByKey = json.loads(docsByKeyStr)

            for subKey in subKeys:
                if subKey not in docsByKey:
                    logger.warning(
                        "Segment %s is missing from index, chunkKey %s",
                        subKey, chunkKey
                    )
                    continue

                # Reconstruct the data
                objectProps: {} = json.loads(docsByKey[subKey])

                # Get out the object type
                thisSegmentTypeId = objectProps['_dtid']
                del objectProps['_dtid']

                # Get out the object type
                thisModelSetId = objectProps['_msid']
                del objectProps['_msid']

                # Create the new object
                newObject = GraphDbSegmentTuple()
                foundSegments.append(newObject)

                newObject.key = subKey
                newObject.modelSet = GraphDbModelSet(id=thisModelSetId)
                newObject.segment = objectProps
                

        # Create the vortex message
        return Payload(filt, tuples=foundSegments).makePayloadEnvelope().toVortexMsg()
        '''