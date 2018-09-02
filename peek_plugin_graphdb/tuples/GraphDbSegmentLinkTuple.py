from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet


@addTupleType
class GraphDbSegmentLinkTuple(Tuple):
    """ Segment Link Tuple

    This tuple is the publicly exposed Segment Links

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbSegmentLinkTuple'

    #:  The key of the vertex that joins the two segments
    vertexKey: str = TupleField()

    #:  The segment that this segment links to
    segmentKey: GraphDbModelSet = TupleField()
