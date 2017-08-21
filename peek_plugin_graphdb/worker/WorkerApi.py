from typing import List, Dict

from sqlalchemy import select

from peek_plugin_base.storage.StorageUtil import makeCoreValuesSubqueryCondition, \
    makeOrmValuesSubqueryCondition
from peek_plugin_graphdb._private.storage.GraphDbItem import GraphDbItem
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet, \
    getOrCreateGraphDbModelSet
from peek_plugin_graphdb.tuples.GraphDbDisplayValueTuple import GraphDbDisplayValueTuple
from peek_plugin_graphdb.tuples.GraphDbRawValueTuple import GraphDbRawValueTuple


class WorkerApi:
    """ Worker Api

    This class allows other classes to work with the GraphDB plugin on the
    worker service.

    """
    _FETCH_SIZE = 5000

    @classmethod
    def getGraphDbDisplayValues(cls,
                               ormSession,
                               modelSetName: str,
                               graphDbKeys: List[str]
                               ) -> List[GraphDbRawValueTuple]:
        """ Get Live DB Display Values

        Return an array of items representing the display values from the GraphDB.

        :param ormSession: The SQLAlchemy orm session from the calling code.
        :param modelSetName: The name of the model set to get the keys for
        :param graphDbKeys: An array of GraphDb Keys.

        :returns: An array of tuples.
        """
        if not graphDbKeys:
            return []

        graphDbModelSet = getOrCreateGraphDbModelSet(ormSession, modelSetName)

        graphDbKeys = set(graphDbKeys)  # Remove duplicates if any exist.
        qry = (
            ormSession.query(GraphDbItem)
                .filter(GraphDbItem.modelSetId == graphDbModelSet.id)
                .filter(makeOrmValuesSubqueryCondition(
                ormSession, GraphDbItem.key, list(graphDbKeys)
            ))
                .yield_per(cls._FETCH_SIZE)
        )

        results = []

        for item in qry:
            results.append(
                GraphDbDisplayValueTuple(key=item.key,
                                        displayValue=item.displayValue,
                                        rawValue=item.rawValue,
                                        dataType=item.dataType)
            )

        return results

    @classmethod
    def getGraphDbKeyDatatypeDict(cls, ormSession,
                                 modelSetName: str,
                                 graphDbKeys: List[str]) -> Dict[str, int]:
        """ Get Live DB Display Values

        Return an array of items representing the display values from the GraphDB.

        :param ormSession: The SQLAlchemy orm session from the calling code.
        :param modelSetName: The name of the model set to get the keys for
        :param graphDbKeys: An array of GraphDb Keys.

        :returns: An array of tuples.
        """
        graphDbTable = GraphDbItem.__table__
        modelTable = GraphDbModelSet.__table__

        if not graphDbKeys:
            return {}

        graphDbKeys = list(set(graphDbKeys))  # Remove duplicates if any exist.
        stmt = (select([graphDbTable.c.key, graphDbTable.c.dataType])
                .select_from(graphDbTable
                             .join(modelTable,
                                   graphDbTable.c.modelSetId == modelTable.c.id))
                .where(modelTable.c.name == modelSetName)
                .where(makeCoreValuesSubqueryCondition(
                    ormSession.bind, graphDbTable.c.key, graphDbKeys
                ))
        )
        resultSet = ormSession.execute(stmt)
        return dict(resultSet.fetchall())
