from typing import Dict, List

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from peek_plugin_graphdb.tuples.GraphDbEdgeTuple import GraphDbEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbSegmentLinkTuple import GraphDbSegmentLinkTuple
from peek_plugin_graphdb.tuples.GraphDbVertexTuple import GraphDbVertexTuple


@addTupleType
class GraphDbSegmentTuple(Tuple):
    """ Segment Tuple

    This tuple is the publicly exposed Segment

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbSegmentTuple'

    #:  The unique key of this segment
    key: str = TupleField()

    #:  The model set of this segment
    modelSet: GraphDbModelSet = TupleField()

    #:  The edges
    edges: List[GraphDbEdgeTuple] = TupleField([])

    #:  The edges
    vertexes: List[GraphDbVertexTuple] = TupleField([])

    #:  The edges
    links: List[GraphDbSegmentLinkTuple] = TupleField([])

