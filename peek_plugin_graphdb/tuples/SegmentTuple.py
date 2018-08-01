from typing import Dict

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb._private.storage.GraphDbSegmentTypeTuple import \
    GraphDbSegmentTypeTuple
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from vortex.Tuple import Tuple, addTupleType, TupleField


@addTupleType
class SegmentTuple(Tuple):
    """ Segment Tuple

    This tuple is the publicly exposed Segment

    """
    __tupleType__ = graphDbTuplePrefix + 'SegmentTuple'

    #:  The unique key of this segment
    key: str = TupleField()

    #:  The model set of this segment
    modelSet: GraphDbModelSet = TupleField()

    #:  The segment type
    segmentType: GraphDbSegmentTypeTuple = TupleField()

    #:  The segment data
    segment: Dict = TupleField()
