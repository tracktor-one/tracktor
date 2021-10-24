class ApiError(Exception):
    """
    Base exception for all exceptions which could occur in the api
    """

    def __init__(self, message="", response_code=500):
        self.response_code = response_code
        self.message = message
        super().__init__(self.message)


class PlaylistNotFound(ApiError):
    def __init__(self, message=""):
        self.response_code = 404
        self.message = message
        super().__init__(self.message, self.response_code)


class PlaylistItemConflict(ApiError):
    def __init__(self, message=""):
        self.response_code = 409
        self.message = message
        super().__init__(self.message, self.response_code)
