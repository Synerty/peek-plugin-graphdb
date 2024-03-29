import logging

from peek_plugin_base.worker.PluginWorkerEntryHookABC import PluginWorkerEntryHookABC
from peek_plugin_graphdb._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_graphdb._private.tuples import loadPrivateTuples
from peek_plugin_graphdb._private.worker.tasks import (
    SegmentIndexCompilerTask,
    SegmentIndexImporterTask,
    TraceConfigImporterTask,
    ItemKeyIndexCompilerTask,
    ItemKeyIndexImporterTask,
)
from peek_plugin_graphdb.tuples import loadPublicTuples

logger = logging.getLogger(__name__)


class WorkerEntryHook(PluginWorkerEntryHookABC):
    def load(self):
        loadPrivateTuples()
        loadStorageTuples()
        loadPublicTuples()
        logger.debug("loaded")

    def start(self):
        logger.debug("started")

    def stop(self):
        logger.debug("stopped")

    def unload(self):
        logger.debug("unloaded")

    @property
    def celeryAppIncludes(self):
        return [
            TraceConfigImporterTask.__name__,
            SegmentIndexImporterTask.__name__,
            SegmentIndexCompilerTask.__name__,
            ItemKeyIndexImporterTask.__name__,
            ItemKeyIndexCompilerTask.__name__,
        ]
