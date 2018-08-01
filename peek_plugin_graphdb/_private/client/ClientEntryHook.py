import logging

from twisted.internet.defer import inlineCallbacks

from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC
from peek_plugin_graphdb._private.PluginNames import graphDbFilt, \
    graphDbActionProcessorName
from peek_plugin_graphdb._private.PluginNames import graphDbObservableName
from peek_plugin_graphdb._private.client.TupleDataObservable import \
    makeClientTupleDataObservableHandler
from peek_plugin_graphdb._private.client.controller.SegmentCacheController import \
    SegmentCacheController
from peek_plugin_graphdb._private.client.handlers.SegmentCacheHandler import \
    SegmentCacheHandler
from peek_plugin_graphdb._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_graphdb._private.tuples import loadPrivateTuples
from peek_plugin_graphdb.tuples import loadPublicTuples
from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler
from vortex.handler.TupleDataObserverClient import TupleDataObserverClient

logger = logging.getLogger(__name__)


class ClientEntryHook(PluginClientEntryHookABC):
    def __init__(self, *args, **kwargs):
        """" Constructor """
        # Call the base classes constructor
        PluginClientEntryHookABC.__init__(self, *args, **kwargs)

        #: Loaded Objects, This is a list of all objects created when we start
        self._loadedObjects = []

    def load(self) -> None:
        """ Load

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialiastion steps here.

        """

        loadStorageTuples()

        loadPrivateTuples()
        loadPublicTuples()

        logger.debug("Loaded")

    @inlineCallbacks
    def start(self):
        """ Load

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialisation steps here.

        """

        # ----------------
        # Proxy actions back to the server, we don't process them at all
        self._loadedObjects.append(
            TupleActionProcessorProxy(
                tupleActionProcessorName=graphDbActionProcessorName,
                proxyToVortexName=peekServerName,
                additionalFilt=graphDbFilt)
        )

        # ----------------
        # Provide the devices access to the servers observable
        tupleDataObservableProxyHandler = TupleDataObservableProxyHandler(
            observableName=graphDbObservableName,
            proxyToVortexName=peekServerName,
            additionalFilt=graphDbFilt,
            observerName="Proxy to devices")
        self._loadedObjects.append(tupleDataObservableProxyHandler)

        # ----------------
        #: This is an observer for us (the client) to use to observe data
        # from the server
        serverTupleObserver = TupleDataObserverClient(
            observableName=graphDbObservableName,
            destVortexName=peekServerName,
            additionalFilt=graphDbFilt,
            observerName="Data for client"
        )
        self._loadedObjects.append(serverTupleObserver)

        # ----------------
        # Segment Cache Controller

        segmentCacheController = SegmentCacheController(
            self.platform.serviceId
        )
        self._loadedObjects.append(segmentCacheController)

        # ----------------
        # Segment Cache Handler

        segmentHandler = SegmentCacheHandler(
            cacheController=segmentCacheController,
            clientId=self.platform.serviceId
        )
        self._loadedObjects.append(segmentHandler)

        # ----------------
        # Set the caches reference to the handler
        segmentCacheController.setSegmentCacheHandler(segmentHandler)

        # ----------------
        # Create the Tuple Observer
        makeClientTupleDataObservableHandler(tupleDataObservableProxyHandler,
                                             segmentCacheController)

        # ----------------
        # Start the compiler controllers
        yield segmentCacheController.start()

        logger.debug("Started")

    def stop(self):
        """ Stop

        This method is called by the platform to tell the peek app to shutdown and stop
        everything it's doing
        """
        # Shutdown and dereference all objects we constructed when we started
        while self._loadedObjects:
            self._loadedObjects.pop().shutdown()

        logger.debug("Stopped")

    def unload(self):
        """Unload

        This method is called after stop is called, to unload any last resources
        before the PLUGIN is unlinked from the platform

        """
        logger.debug("Unloaded")
