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
    ACTION_STOP_TRACE = 1
    ACTION_CONTINUE_TRACE = 2
    ACTION_ABORT_TRACE_WITH_MESSAGE = 3

    #: Data to go with actions that require it
    actionData: str = TupleField(1)

    #: The name of the property to apply the rule to
    propertyName: str = TupleField()

    #:  A comma separated list of property values to match
    propertyValue: str = TupleField()

    #:  The type of value in the property value
    propertyValueType: int = TupleField(1)
    PROP_VAL_TYPE_SIMPLE = 1
    PROP_VAL_TYPE_COMMA_LIST = 2
    PROP_VAL_TYPE_REGEX = 3
    PROP_VAL_TYPE_BITMASK_AND = 4

    #:  The comment for this rule
    comment: str = TupleField()

    #:  Is this rule enabled
    isEnabled: bool = TupleField(True)