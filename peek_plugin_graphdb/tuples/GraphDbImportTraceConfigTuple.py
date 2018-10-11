from vortex.Tuple import addTupleType, TupleField

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb.tuples.GraphDbTraceConfigTuple import GraphDbTraceConfigTuple


@addTupleType
class GraphDbImportTraceConfigTuple(GraphDbTraceConfigTuple):
    """ Import TraceConfig Tuple

    This tuple is the publicly exposed TraceConfig

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbImportTraceConfigTuple'

    #:  The hash of this import group  [Required]
    importGroupHash: str = TupleField()


