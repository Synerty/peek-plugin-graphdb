
from peek_plugin_graphdb._private.PluginNames import graphdbTuplePrefix
from sqlalchemy import Column
from sqlalchemy import Integer, String
from vortex.Tuple import addTupleType, Tuple, TupleField

from .DeclarativeBase import DeclarativeBase


@addTupleType
class GraphDbModelSet(Tuple, DeclarativeBase):
    __tablename__ = 'GraphDbModelSet'
    __tupleType__ = graphdbTuplePrefix + __tablename__

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    comment = Column(String)

    propsJson = Column(String(500))


def getOrCreateGraphDbModelSet(session, modelSetName:str) -> GraphDbModelSet:
    qry = session.query(GraphDbModelSet).filter(GraphDbModelSet.name == modelSetName)
    if not qry.count():
        session.add(GraphDbModelSet(name=modelSetName))
        session.commit()

    return qry.one()
