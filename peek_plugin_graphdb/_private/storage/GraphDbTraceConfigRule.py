from typing import Optional

from sqlalchemy import Column, ForeignKey, Boolean
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from vortex.Tuple import Tuple, addTupleType

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb._private.storage.DeclarativeBase import DeclarativeBase
from peek_plugin_graphdb.tuples.GraphDbTraceConfigRuleTuple import \
    GraphDbTraceConfigRuleTuple


@addTupleType
class GraphDbTraceConfigRule(Tuple, DeclarativeBase):
    __tupleType__ = graphDbTuplePrefix + 'GraphDbTraceConfigRuleTable'
    __tablename__ = 'GraphDbTraceConfigRule'

    #:  The unique ID of this segment (database generated)
    id = Column(Integer, primary_key=True, autoincrement=True)

    #:  The model set for this segment
    traceConfigId = Column(Integer,
                           ForeignKey('GraphDbTraceConfig.id', ondelete='CASCADE'),
                           nullable=False)
    traceConfig = relationship('GraphDbTraceConfig')

    #:  The processing order of this rule
    order = Column(Integer, nullable=False)

    #:  What should this rule look for
    applyTo = Column(Integer, nullable=False)

    #:  What should this rule look for
    action = Column(Integer, nullable=False)

    #: The name of the property to apply the rule to
    propertyName = Column(String, nullable=False)

    #:  A comma separated list of property values to match
    propertyValues = Column(String, nullable=False)

    #:  Stop = True, Continue = False
    propertyValueType = Column(Integer, nullable=False)

    #:  The comment for this rule
    comment = Column(String)

    #:  Is this rule enabled
    isEnabled = Column(Boolean, nullable=False, server_default="true")

    def fromTuple(self, tupleIn: GraphDbTraceConfigRuleTuple,
                  traceConfigId: Optional[int]) -> 'GraphDbTraceConfigRule':
        if traceConfigId is not None:
            self.traceConfigId = traceConfigId

        self.order = tupleIn.order
        self.applyTo = tupleIn.applyTo
        self.action = tupleIn.action
        self.propertyName = tupleIn.propertyName
        self.propertyValues = tupleIn.propertyValues
        self.propertyValueType = tupleIn.propertyValueType
        self.comment = tupleIn.comment
        self.isEnabled = tupleIn.isEnabled

        return self

    def toTuple(self) -> GraphDbTraceConfigRuleTuple:
        traceTuple = GraphDbTraceConfigRuleTuple(
            order=self.order,
            applyTo=self.applyTo,
            action=self.action,
            propertyName=self.propertyName,
            propertyValues=self.propertyValues,
            propertyValueType=self.propertyValueType,
            comment=self.comment,
            isEnabled=self.isEnabled
        )

        traceTuple.rules = [rule.toTuple() for rule in self.rules]

        return traceTuple
