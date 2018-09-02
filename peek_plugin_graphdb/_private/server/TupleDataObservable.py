from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.PluginNames import graphDbObservableName
from peek_plugin_graphdb._private.server.tuple_providers.ModelSetTupleProvider import \
    ModelSetTupleProvider
from peek_plugin_graphdb._private.storage.GraphDbSegment import GraphDbSegment
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from peek_plugin_graphdb._private.tuples.AdminStatusTuple import AdminStatusTuple
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from .controller.StatusController import StatusController
from .tuple_providers.AdminStatusTupleProvider import AdminStatusTupleProvider


def makeTupleDataObservableHandler(dbSessionCreator: DbSessionCreator,
                                   statusController: StatusController):
    """" Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param dbSessionCreator: A function that returns a SQLAlchemy session when called
    :param statusController:

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=graphDbObservableName,
        additionalFilt=graphDbFilt)

    # Admin status tuple
    tupleObservable.addTupleProvider(AdminStatusTuple.tupleName(),
                                     AdminStatusTupleProvider(statusController))

    # Model Set Tuple
    tupleObservable.addTupleProvider(GraphDbModelSet.tupleName(),
                                     ModelSetTupleProvider(dbSessionCreator))

    return tupleObservable
