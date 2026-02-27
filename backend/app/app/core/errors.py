class CustomBaseError(Exception):
    """Base class for all errors that are safe to forward to the client"""

    def __init__(self, message=None, status_code=500):
        super().__init__(message)
        self.status_code = status_code
