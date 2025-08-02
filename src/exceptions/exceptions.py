class BuklatApiError(Exception):
    """Base exception class for the Buklat API."""

    def __init__(
        self, message: str = "Service is unavailable.", name: str = "BuklatApi"
    ):
        self.message = message
        self.name = name
        super().__init__(self.message, self.name)


class ServiceError(BuklatApiError):
    """External service or DB failure."""

    pass


class EntityAlreadyExistsError(BuklatApiError):
    """Entity already exists."""

    pass


class EntityDoesNotExistError(BuklatApiError):
    """Entity not found."""

    pass


class RegistrationFailed(BuklatApiError):
    """Registration failed."""

    pass


class AuthenticationFailed(BuklatApiError):
    """Invalid username or password."""

    pass


class InvalidTokenError(BuklatApiError):
    """Invalid or expired token."""

    pass


class InvalidAccountError(BuklatApiError):
    """Account has been disabled or deactivated."""

    pass
