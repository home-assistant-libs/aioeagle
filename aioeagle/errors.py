class EagleError(Exception):
    """Base error."""


class BadAuth(EagleError):
    """Authentication not accepted."""
