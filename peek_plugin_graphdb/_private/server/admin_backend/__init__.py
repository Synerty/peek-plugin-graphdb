from peek_plugin_graphdb._private.server.admin_backend.EditItemKeyTypeHandler import \
    makeItemKeyTypeHandler
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from .SettingPropertyHandler import makeSettingPropertyHandler
from .ViewSegmentHandler import makeSegmentTableHandler


def makeAdminBackendHandlers(tupleObservable: TupleDataObservableHandler,
                             dbSessionCreator):
    yield makeSegmentTableHandler(tupleObservable, dbSessionCreator)

    yield makeSettingPropertyHandler(dbSessionCreator)
    yield makeItemKeyTypeHandler(tupleObservable, dbSessionCreator)

