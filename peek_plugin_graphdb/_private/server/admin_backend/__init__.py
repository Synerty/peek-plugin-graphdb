from peek_plugin_graphdb._private.server.admin_backend.EditSegmentPropertyHandler import \
    makeSegmentPropertyHandler
from peek_plugin_graphdb._private.server.admin_backend.EditSegmentTypeHandler import \
    makeSegmentTypeHandler
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from .SettingPropertyHandler import makeSettingPropertyHandler
from .ViewSegmentHandler import makeSegmentTableHandler


def makeAdminBackendHandlers(tupleObservable: TupleDataObservableHandler,
                             dbSessionCreator):
    yield makeSegmentTableHandler(tupleObservable, dbSessionCreator)

    yield makeSettingPropertyHandler(dbSessionCreator)

    yield makeSegmentPropertyHandler(tupleObservable, dbSessionCreator)

    yield makeSegmentTypeHandler(tupleObservable, dbSessionCreator)
