from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from vortex.Tuple import addTupleType, TupleField, Tuple


@addTupleType
class AdminStatusTuple(Tuple):
    __tupleType__ = graphDbTuplePrefix + "AdminStatusTuple"

    segmentCompilerQueueStatus: bool = TupleField(False)
    segmentCompilerQueueSize: int = TupleField(0)
    segmentCompilerQueueProcessedTotal: int = TupleField(0)
    segmentCompilerQueueLastError: str = TupleField()
