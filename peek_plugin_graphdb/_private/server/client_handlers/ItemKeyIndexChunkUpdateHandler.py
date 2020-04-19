import logging
from typing import Dict

from peek_abstract_chunked_index.private.server.client_handlers.ChunkedIndexChunkUpdateHandlerABC import \
    ChunkedIndexChunkUpdateHandlerABC
from peek_abstract_chunked_index.private.tuples.ChunkedIndexEncodedChunkTupleABC import \
    ChunkedIndexEncodedChunkTupleABC
from peek_plugin_graphdb._private.client.controller.ItemKeyIndexCacheController import \
    clientItemKeyIndexUpdateFromServerFilt
from peek_plugin_graphdb._private.storage.ItemKeyIndexEncodedChunk import \
    ItemKeyIndexEncodedChunk

logger = logging.getLogger(__name__)


class ItemKeyIndexChunkUpdateHandler(ChunkedIndexChunkUpdateHandlerABC):
    _ChunkedTuple: ChunkedIndexEncodedChunkTupleABC = ItemKeyIndexEncodedChunk
    _updateFromServerFilt: Dict = clientItemKeyIndexUpdateFromServerFilt
    _logger: logging.Logger = logger