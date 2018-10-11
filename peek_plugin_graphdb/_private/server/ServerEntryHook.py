import logging

from celery import Celery

from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import \
    PluginServerStorageEntryHookABC
from peek_plugin_base.server.PluginServerWorkerEntryHookABC import \
    PluginServerWorkerEntryHookABC
from peek_plugin_graphdb._private.server.api.GraphDbApi import GraphDbApi
from peek_plugin_graphdb._private.server.client_handlers.ClientSegmentChunkLoadRpc import \
    ClientSegmentChunkLoadRpc
from peek_plugin_graphdb._private.server.client_handlers.ClientSegmentChunkUpdateHandler import \
    ClientSegmentChunkUpdateHandler
from peek_plugin_graphdb._private.server.client_handlers.ClientTraceConfigLoadRpc import \
    ClientTraceConfigLoadRpc
from peek_plugin_graphdb._private.server.client_handlers.ClientTraceConfigUpdateHandler import \
    ClientTraceConfigUpdateHandler
from peek_plugin_graphdb._private.server.controller.ChunkCompilerQueueController import \
    ChunkCompilerQueueController
from peek_plugin_graphdb._private.server.controller.ImportController import ImportController
from peek_plugin_graphdb._private.server.controller.StatusController import StatusController
from peek_plugin_graphdb._private.storage import DeclarativeBase
from peek_plugin_graphdb._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_graphdb._private.tuples import loadPrivateTuples
from peek_plugin_graphdb.tuples import loadPublicTuples
from peek_plugin_graphdb.tuples.GraphDbSegmentTuple import GraphDbSegmentTuple
from peek_plugin_graphdb.tuples.GraphDbImportSegmentTuple import GraphDbImportSegmentTuple
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload
from .TupleActionProcessor import makeTupleActionProcessorHandler
from .TupleDataObservable import makeTupleDataObservableHandler
from .admin_backend import makeAdminBackendHandlers
from .controller.MainController import MainController

logger = logging.getLogger(__name__)


class ServerEntryHook(PluginServerEntryHookABC,
                      PluginServerStorageEntryHookABC,
                      PluginServerWorkerEntryHookABC):
    def __init__(self, *args, **kwargs):
        """" Constructor """
        # Call the base classes constructor
        PluginServerEntryHookABC.__init__(self, *args, **kwargs)

        #: Loaded Objects, This is a list of all objects created when we start
        self._loadedObjects = []

        self._api = None

    def load(self) -> None:
        """ Load

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialiastion steps here.

        """
        loadStorageTuples()
        loadPrivateTuples()
        loadPublicTuples()
        logger.debug("Loaded")

    @property
    def dbMetadata(self):
        return DeclarativeBase.metadata

    def start(self):
        """ Start

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialiastion steps here.

        """

        # ----------------
        # Client Handlers and RPC

        self._loadedObjects += ClientSegmentChunkLoadRpc(self.dbSessionCreator).makeHandlers()
        self._loadedObjects += ClientTraceConfigLoadRpc(self.dbSessionCreator).makeHandlers()

        # ----------------
        # Client Graph Segment client update handler
        clientSegmentChunkUpdateHandler = ClientSegmentChunkUpdateHandler(
            self.dbSessionCreator
        )
        self._loadedObjects.append(clientSegmentChunkUpdateHandler)

        # ----------------
        # Client Search Object client update handler
        clientTraceConfigUpdateHandler = ClientTraceConfigUpdateHandler(
            self.dbSessionCreator
        )
        self._loadedObjects.append(clientTraceConfigUpdateHandler)

        # ----------------
        # Status Controller
        statusController = StatusController()
        self._loadedObjects.append(statusController)

        # ----------------
        # Tuple Observable
        tupleObservable = makeTupleDataObservableHandler(
            dbSessionCreator=self.dbSessionCreator,
            statusController=statusController
        )
        self._loadedObjects.append(tupleObservable)

        # ----------------
        # Admin Handler
        self._loadedObjects.extend(
            makeAdminBackendHandlers(tupleObservable, self.dbSessionCreator)
        )

        # ----------------
        # Tell the status controller about the Tuple Observable
        statusController.setTupleObservable(tupleObservable)

        # ----------------
        # Main Controller
        mainController = MainController(
            dbSessionCreator=self.dbSessionCreator,
            tupleObservable=tupleObservable)

        self._loadedObjects.append(mainController)

        # ----------------
        # Search Object Controller
        searchObjectChunkCompilerQueueController = ChunkCompilerQueueController(
            dbSessionCreator=self.dbSessionCreator,
            statusController=statusController,
            clientChunkUpdateHandler=clientSegmentChunkUpdateHandler
        )
        self._loadedObjects.append(searchObjectChunkCompilerQueueController)

        # ----------------
        # Import Controller
        importController = ImportController(clientTraceConfigUpdateHandler)
        self._loadedObjects.append(importController)

        # ----------------
        # Setup the Action Processor
        self._loadedObjects.append(makeTupleActionProcessorHandler(mainController))

        # ----------------
        # Setup the APIs
        # Initialise the API object that will be shared with other plugins
        self._api = GraphDbApi(importController)
        self._loadedObjects.append(self._api)

        # ----------------
        # Start the compiler controllers
        searchObjectChunkCompilerQueueController.start()

        # self._test()

        logger.debug("Started")

    def _test(self):
        # ----------------
        # API test
        newDocs = []
        so1 = GraphDbImportSegmentTuple(
            key="doc1key",
            modelSetKey="testModel",
            segmentTypeKey="objectType1",
            importGroupHash='test load',
            segment={
                "name": "134 Ocean Parade, Circuit breaker 1",
                "alias": "SO1ALIAS",
                "propStr": "Test Property 1",
                "propNumArr": [1, 2, 4, 5, 6],
                "propStrArr": ["one", "two", "three", "four"]
            }
        )

        newDocs.append(so1)
        so2 = GraphDbImportSegmentTuple(
            key="doc2key",
            modelSetKey="testModel",
            segmentTypeKey="objectType2",
            importGroupHash='test load',
            segment={
                "name": "69 Sheep Farmers Rd Sub TX breaker",
                "alias": "SO2ALIAS",
                "propStr": "Test Property 1",
                "propNumArr": [7,8,9,10,11],
                "propStrArr": ["five", "siz", "seven", "eight"]
            }
        )

        newDocs.append(so2)

        d = Payload(tuples=newDocs).toEncodedPayloadDefer()
        d.addCallback(self._api.createOrUpdateSegments)
        d.addErrback(vortexLogFailure, logger, consumeError=True)

    def stop(self):
        """ Stop

        This method is called by the platform to tell the peek app to shutdown and stop
        everything it's doing
        """
        # Shutdown and dereference all objects we constructed when we started
        while self._loadedObjects:
            self._loadedObjects.pop().shutdown()

        self._api = None

        logger.debug("Stopped")

    def unload(self):
        """Unload

        This method is called after stop is called, to unload any last resources
        before the PLUGIN is unlinked from the platform

        """
        logger.debug("Unloaded")

    @property
    def publishedServerApi(self) -> object:
        """ Published Server API
    
        :return  class that implements the API that can be used by other Plugins on this
        platform service.
        """
        return self._api

    ###### Implement PluginServerWorkerEntryHookABC

    @property
    def celeryApp(self) -> Celery:
        from peek_plugin_graphdb._private.worker.CeleryApp import celeryApp
        return celeryApp
