import logging
from typing import List, Dict

from sqlalchemy import select

from peek_abstract_chunked_index.private.server.client_handlers.ChunkedIndexChunkUpdateHandlerABC import \
    ChunkedIndexChunkUpdateHandlerABC
from peek_abstract_chunked_index.private.tuples.ChunkedIndexEncodedChunkTupleABC import \
    ChunkedIndexEncodedChunkTupleABC
from peek_plugin_graphdb._private.client.controller.SegmentCacheController import \
    clientSegmentUpdateFromServerFilt
from peek_plugin_graphdb._private.storage.GraphDbEncodedChunk import GraphDbEncodedChunk
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet

logger = logging.getLogger(__name__)


class SegmentChunkIndexUpdateHandler(ChunkedIndexChunkUpdateHandlerABC):
    _ChunkedTuple: ChunkedIndexEncodedChunkTupleABC = GraphDbEncodedChunk
    _updateFromServerFilt: Dict = clientSegmentUpdateFromServerFilt
    _logger: logging.Logger = logger

    def _makeLoadSql(self, chunkKeys: List[str]):
        chunkTable = GraphDbEncodedChunk.__table__
        msTable = GraphDbModelSet.__table__

        return select([msTable.c.key,
                       chunkTable.c.chunkKey,
                       chunkTable.c.encodedData,
                       chunkTable.c.encodedHash,
                       chunkTable.c.lastUpdate]) \
            .select_from(chunkTable.join(msTable)) \
            .where(chunkTable.c.indexBucket.in_(chunkKeys))
