import logging
from typing import List

from peek_abstract_chunked_index.private.server.client_handlers.ACIChunkLoadRpcABC import \
    ACIChunkLoadRpcABC
from peek_plugin_base.PeekVortexUtil import peekServerName, peekClientName
from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.storage.ItemKeyIndexEncodedChunk import ItemKeyIndexEncodedChunk
from vortex.rpc.RPC import vortexRPC

logger = logging.getLogger(__name__)


class ItemKeyIndexChunkLoadRpc(ACIChunkLoadRpcABC):

    def makeHandlers(self):
        """ Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of it's self so we can simply yield the result
        of the start method.

        """

        yield self.loadItemKeyIndexChunks.start(funcSelf=self)
        logger.debug("RPCs started")

    # -------------
    @vortexRPC(peekServerName, acceptOnlyFromVortex=peekClientName, timeoutSeconds=60,
               additionalFilt=graphDbFilt, deferToThread=True)
    def loadItemKeyIndexChunks(self, offset: int, count: int) -> List[ItemKeyIndexEncodedChunk]:
        """ Update Page Loader Status

        Tell the server of the latest status of the loader

        """
        return self.ckiInitialLoadChunksBlocking(offset, count, ItemKeyIndexEncodedChunk)