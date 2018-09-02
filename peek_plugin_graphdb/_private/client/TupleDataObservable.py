from peek_plugin_graphdb._private.client.controller.SegmentCacheController import \
    SegmentCacheController
from peek_plugin_graphdb._private.client.tuple_providers.ClientSegmentTupleProvider import \
    ClientSegmentTupleProvider
from peek_plugin_graphdb._private.client.tuple_providers.ClientSegmentUpdateDateTupleProvider import \
    ClientSegmentUpdateDateTupleProvider
from peek_plugin_graphdb._private.tuples.SegmentUpdateDateTuple import \
    SegmentUpdateDateTuple
from peek_plugin_graphdb.tuples.GraphDbSegmentTuple import GraphDbSegmentTuple
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeClientTupleDataObservableHandler(
        tupleObservable: TupleDataObservableProxyHandler,
        cacheHandler: SegmentCacheController):
    """" Make CLIENT Tuple Data Observable Handler

    This method registers the tuple providers for the proxy, that are served locally.

    :param cacheHandler:
    :param tupleObservable: The tuple observable proxy

    """

    tupleObservable.addTupleProvider(GraphDbSegmentTuple.tupleName(),
                                     ClientSegmentTupleProvider(cacheHandler))

    tupleObservable.addTupleProvider(SegmentUpdateDateTuple.tupleName(),
                                     ClientSegmentUpdateDateTupleProvider(cacheHandler))
