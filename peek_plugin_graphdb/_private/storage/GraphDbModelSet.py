from sqlalchemy import Column
from sqlalchemy import Integer, String
from vortex.Tuple import addTupleType, Tuple

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from .DeclarativeBase import DeclarativeBase


@addTupleType
class GraphDbModelSet(Tuple, DeclarativeBase):
    __tablename__ = 'GraphDbModelSet'
    __tupleType__ = graphDbTuplePrefix + __tablename__

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)

    comment = Column(String)
    propsJson = Column(String)


def getOrCreateGraphDbModelSet(session, modelSetName: str) -> GraphDbModelSet:
    qry = session.query(GraphDbModelSet).filter(GraphDbModelSet.name == modelSetName)
    if not qry.count():
        session.add(GraphDbModelSet(name=modelSetName))
        session.commit()

    return qry.one()
