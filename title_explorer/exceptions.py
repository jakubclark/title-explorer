class TitleExplorerException(Exception):

    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code


class TitleNotFound(TitleExplorerException):
    def __init__(self, message):
        super().__init__(message, 404)
