class CustomConnectionError(Exception):
    # TODO: why is message added twice every time? Multithreading?
    def __init__(self, exc: str, message: str = ""):
        message = exc.split(" (")[0]
        super().__init__(message)


class InvalidUrl(Exception):
    def __init__(self, exc: str, message: str = ""):
        message = exc.split(":")[0]
        super().__init__(message)


class UnhandledRequestMethod(Exception):
    def __init__(
        self, method: str, message="Unhandled request method used: %s. Shutting down."
    ):
        message = message % method
        super().__init__(message)


class UnhandledException(Exception):
    def __init__(self, message="Unexpected error occurred. Shutting down."):
        super().__init__(message)