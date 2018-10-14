from peek_plugin_graphdb._private.client.controller.ItemKeyIndexCacheController import \
    ItemKeyIndexCacheController
from peek_plugin_graphdb._private.client.controller.SegmentCacheController import \
    SegmentCacheController
from peek_plugin_graphdb._private.client.controller.TraceConfigCacheController import \
    TraceConfigCacheController
from peek_plugin_graphdb._private.client.tuple_providers.ItemKeyIndexUpdateDateTupleProvider import \
    ItemKeyIndexUpdateDateTupleProvider
from peek_plugin_graphdb._private.client.tuple_providers.SegmentUpdateDateTupleProvider import \
    SegmentUpdateDateTupleProvider
from peek_plugin_graphdb._private.client.tuple_providers.TraceConfigTupleProvider import \
    TraceConfigTupleProvider
from peek_plugin_graphdb._private.client.tuple_providers.TraceResultTupleProvider import \
    TraceResultTupleProvider
from peek_plugin_graphdb._private.tuples.ItemKeyIndexUpdateDateTuple import \
    ItemKeyIndexUpdateDateTuple
from peek_plugin_graphdb._private.tuples.SegmentIndexUpdateDateTuple import \
    SegmentIndexUpdateDateTuple
from peek_plugin_graphdb.tuples.GraphDbSegmentTuple import GraphDbSegmentTuple
from peek_plugin_graphdb.tuples.GraphDbTraceConfigTuple import GraphDbTraceConfigTuple
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeClientTupleDataObservableHandler(
        tupleObservable: TupleDataObservableProxyHandler,
        segmentCacheHandler: SegmentCacheController,
        itemKeyCacheHandler: ItemKeyIndexCacheController,
        traceConfigCacheHandler: TraceConfigCacheController):
    """" Make CLIENT Tuple Data Observable Handler

    This method registers the tuple providers for the proxy, that are served locally.

    :param segmentCacheHandler:
    :param traceConfigCacheHandler:
    :param tupleObservable: The tuple observable proxy

    """

    tupleObservable.addTupleProvider(
        GraphDbSegmentTuple.tupleName(),
        TraceResultTupleProvider(segmentCacheHandler,
                                 itemKeyCacheHandler,
                                 traceConfigCacheHandler)
    )

    tupleObservable.addTupleProvider(
        SegmentIndexUpdateDateTuple.tupleName(),
        SegmentUpdateDateTupleProvider(segmentCacheHandler)
    )

    tupleObservable.addTupleProvider(
        GraphDbTraceConfigTuple.tupleName(),
        TraceConfigTupleProvider(traceConfigCacheHandler)
    )

    tupleObservable.addTupleProvider(ItemKeyIndexUpdateDateTuple.tupleName(),
                                     ItemKeyIndexUpdateDateTupleProvider(
                                         itemKeyCacheHandler))
