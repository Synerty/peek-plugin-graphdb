import logging

logger = logging.getLogger(__name__)


class GraphDbController(object):

    def __init__(self, dbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    def shutdown(self):
        pass
