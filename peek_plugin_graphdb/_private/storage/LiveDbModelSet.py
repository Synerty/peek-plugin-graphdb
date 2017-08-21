
from peek_plugin_graphdb._private.PluginNames import graphdbTuplePrefix
from sqlalchemy import Column
from sqlalchemy import Integer, String
from vortex.Tuple import addTupleType, Tuple, TupleField

from .DeclarativeBase import DeclarativeBase


@addTupleType
class LiveDbModelSet(Tuple, DeclarativeBase):
    __tablename__ = 'LiveDbModelSet'
    __tupleType__ = graphdbTuplePrefix + __tablename__

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    comment = Column(String)

    propsJson = Column(String(500))


def getOrCreateLiveDbModelSet(session, modelSetName:str) -> LiveDbModelSet:
    qry = session.query(LiveDbModelSet).filter(LiveDbModelSet.name == modelSetName)
    if not qry.count():
        session.add(LiveDbModelSet(name=modelSetName))
        session.commit()

    return qry.one()
