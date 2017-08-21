from vortex.handler.TupleActionProcessor import TupleActionProcessor

from peek_plugin_graphdb._private.PluginNames import graphdbFilt
from peek_plugin_graphdb._private.PluginNames import graphdbActionProcessorName
from .controller.MainController import MainController


def makeTupleActionProcessorHandler(mainController: MainController):
    processor = TupleActionProcessor(
        tupleActionProcessorName=graphdbActionProcessorName,
        additionalFilt=graphdbFilt,
        defaultDelegate=mainController)
    return processor
