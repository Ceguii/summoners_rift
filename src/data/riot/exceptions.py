class RiotAPIError(Exception):
    def __init__(
        self, message: str, status_code: int | None = None, url: str | None = None
    ):
        self.message = message
        self.status_code = status_code
        self.url = url
        super().__init__(message)

    def __str__(self):
        return f"{self.message} (status={self.status_code}, url={self.url})"


class RiotNotFoundError(RiotAPIError):
    """404 - Resource not found"""

    pass


class RiotForbiddenError(RiotAPIError):
    """403 - Invalid API key or forbidden"""

    pass


class RiotRateLimitError(RiotAPIError):
    """429 - Rate limit exceeded"""

    pass


class RiotServerError(RiotAPIError):
    """5xx - Riot server error"""

    pass


class RiotTimeoutError(RiotAPIError):
    pass


class RiotConnectionError(RiotAPIError):
    pass
