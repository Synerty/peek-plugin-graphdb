import logging

from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.storage.GraphDbPropertyTuple import GraphDbPropertyTuple
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandler, OrmCrudHandlerExtension

logger = logging.getLogger(__name__)

# This dict matches the definition in the Admin angular app.
filtKey = {"key": "admin.Edit.GraphDbPropertyTuple"}
filtKey.update(graphDbFilt)


# This is the CRUD hander‰
class __CrudHandler(OrmCrudHandler):
    pass


class __ExtUpdateObservable(OrmCrudHandlerExtension):
    """ Update Observable ORM Crud Extension

    This extension is called after events that will alter data,
    it then notifies the observer.

    """
    def __init__(self, tupleDataObserver: TupleDataObservableHandler):
        self._tupleDataObserver = tupleDataObserver

    def _tellObserver(self, tuple_, tuples, session, payloadFilt):
        self._tupleDataObserver.notifyOfTupleUpdate(
            TupleSelector(GraphDbPropertyTuple.tupleName(), {})
        )
        return True

    afterUpdateCommit = _tellObserver
    afterDeleteCommit = _tellObserver


# This method creates an instance of the handler class.
def makeSegmentPropertyHandler(tupleObservable, dbSessionCreator):
    handler = __CrudHandler(dbSessionCreator, GraphDbPropertyTuple,
                            filtKey, retreiveAll=True)

    logger.debug("Started")
    handler.addExtension(GraphDbPropertyTuple, __ExtUpdateObservable(tupleObservable))
    return handler
