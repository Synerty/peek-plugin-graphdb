from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix


@addTupleType
class ItemKeyTypeTuple(Tuple):
    """ ItemKeyIndex Tuple

    This tuple is the publicly exposed ItemKeyIndex

    """
    __tupleType__ = graphDbTuplePrefix + 'ItemKeyTypeTuple'

    #:  A protected variable
    id__: int = TupleField()

    #:  The unique key of this itemKeyIndex
    key: str = TupleField()

    #:  The model set key of this itemKeyIndex
    modelSetKey: str = TupleField()

    #:  The unique title of itemKeyIndex
    name: str = TupleField()
