from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler

from peek_plugin_graphdb._private.client.controller.SegmentCacheController import \
    SegmentCacheController
from peek_plugin_graphdb._private.client.controller.TraceConfigCacheController import \
    TraceConfigCacheController
from peek_plugin_graphdb._private.client.tuple_providers.ClientSegmentUpdateDateTupleProvider import \
    ClientSegmentUpdateDateTupleProvider
from peek_plugin_graphdb._private.client.tuple_providers.ClientTraceConfigTupleProvider import \
    ClientTraceConfigTupleProvider
from peek_plugin_graphdb._private.client.tuple_providers.ClientTraceResultTupleProvider import \
    ClientTraceResultTupleProvider
from peek_plugin_graphdb._private.tuples.SegmentUpdateDateTuple import \
    SegmentUpdateDateTuple
from peek_plugin_graphdb.tuples.GraphDbSegmentTuple import GraphDbSegmentTuple
from peek_plugin_graphdb.tuples.GraphDbTraceConfigTuple import GraphDbTraceConfigTuple


def makeClientTupleDataObservableHandler(
        tupleObservable: TupleDataObservableProxyHandler,
        segmentCacheHandler: SegmentCacheController,
        traceConfigCacheHandler: TraceConfigCacheController):
    """" Make CLIENT Tuple Data Observable Handler

    This method registers the tuple providers for the proxy, that are served locally.

    :param segmentCacheHandler:
    :param traceConfigCacheHandler:
    :param tupleObservable: The tuple observable proxy

    """

    tupleObservable.addTupleProvider(
        GraphDbSegmentTuple.tupleName(),
        ClientTraceResultTupleProvider(segmentCacheHandler, traceConfigCacheHandler)
    )

    tupleObservable.addTupleProvider(
        SegmentUpdateDateTuple.tupleName(),
        ClientSegmentUpdateDateTupleProvider(segmentCacheHandler)
    )

    tupleObservable.addTupleProvider(
        GraphDbTraceConfigTuple.tupleName(),
        ClientTraceConfigTupleProvider(traceConfigCacheHandler)
    )
