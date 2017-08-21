from peek_plugin_graphdb._private.PluginNames import graphdbFilt
from peek_plugin_graphdb._private.PluginNames import graphdbObservableName
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler


def makeTupleDataObservableHandler(ormSessionCreator):
    """" Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param ormSessionCreator: A function that returns a SQLAlchemy session when called

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=graphdbObservableName,
        additionalFilt=graphdbFilt)

    # # Register TupleProviders here
    # tupleObservable.addTupleProvider(StringIntTuple.tupleName(),
    #                                  StringIntTupleProvider(ormSessionCreator))
    return tupleObservable
