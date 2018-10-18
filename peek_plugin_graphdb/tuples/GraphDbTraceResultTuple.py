from typing import List, Optional

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb.tuples.GraphDbImportEdgeTuple import GraphDbImportEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbImportVertexTuple import GraphDbImportVertexTuple


@addTupleType
class GraphDbTraceResultTuple(Tuple):
    """ GraphDB Trace Result Tuple

    This tuple contains the result of running a trace on the model

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbTraceResultTuple'

    #:  The key of the model set that the result was created with.
    modelSetKey: str = TupleField()

    #:  The key of the Trace Config
    traceConfigKey: str = TupleField()

    #:  The key of the vertex start point of this trace
    startVertexKey: str = TupleField()

    #:  The edges
    edges: List[GraphDbEdgeTuple] = TupleField([])

    #:  The vertexes
    vertexes: List[GraphDbImportVertexTuple] = TupleField([])

    #:  The message if the trace was aborted
    traceAbortedMessage: Optional[str] = TupleField()
