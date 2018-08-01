from typing import Dict

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from vortex.Tuple import addTupleType, TupleField, Tuple


@addTupleType
class ImportSegmentTuple(Tuple):
    """ Import Segment Tuple

    This tuple is the publicly exposed Segment

    """
    __tupleType__ = graphDbTuplePrefix + 'ImportSegmentTuple'

    #:  The unique key of this segment
    key: str = TupleField()

    #:  The model set of this segment
    modelSetKey: str = TupleField()

    #:  The segment type
    segmentTypeKey: str = TupleField()

    #:  The segment data
    segment: Dict = TupleField()

    #:  The hash of this import group
    importGroupHash: str = TupleField()
