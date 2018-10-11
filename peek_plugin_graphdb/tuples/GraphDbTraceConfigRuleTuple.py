from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix


@addTupleType
class GraphDbTraceConfigRuleTuple(Tuple):
    """ Import Graph Trace Config Rule

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbImportTraceConfigRuleTuple'

    #:  The processing order of this rule
    order: int = TupleField()

    #:  What should this rule look for
    applyTo: int = TupleField(1)
    APPLY_TO_VERTEX = 1
    APPLY_TO_EDGE = 2

    #:  What action should be taken when this rule is met
    action: int = TupleField(1)
    ACTION_STOP = 1
    ACTION_CONTINUE = 2

    #: The name of the property to apply the rule to
    propertyName: str = TupleField()

    #:  A comma separated list of property values to match
    propertyValues: str = TupleField()

    #:  The type of value in the property value
    propertyValueType: int = TupleField(1)
    PROP_VAL_TYPE_SIMPLE = 1
    PROP_VAL_TYPE_COMMA_LIST = 2
    PROP_VAL_TYPE_REGEX = 3

    #:  The comment for this rule
    comment: str = TupleField()

    #:  Is this rule enabled
    isEnabled: bool = TupleField(True)
