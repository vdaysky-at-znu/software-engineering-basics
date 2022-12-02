from typing import Any, Dict
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.util import response


class APIError(Exception):
    status_code: int = None
    message: str = None
    error_code: int = None
    headers: dict = None

    def __init__(
            self,
            message: str = None,
            *,
            status_code: int = None,
            error_code: int = None,
            headers: Dict[str, Any] = None,
    ):
        if not message and not self.message:
            raise ValueError('`message` is required')

        if not status_code and not self.status_code:
            raise ValueError('`status_code` is required')

        self.status_code = status_code or self.status_code
        self.message = message or self.message
        self.error_code = error_code or self.error_code
        self.headers = headers or self.headers


class AuthorizationError(APIError):
    status_code = 401


class InvalidAdminAPIKeyError(AuthorizationError):
    message = 'Valid admin API key is required.'


class InvalidAPIKeyError(AuthorizationError):
    message = 'Valid API key is required.'


class InvalidWalletAuthError(AuthorizationError):
    message = 'Valid wallet auth token is required.'


class PermissionError(APIError):
    status_code = 403


class BadRequestError(APIError):
    status_code = 400


class NotFoundError(APIError):
    status_code = 404


class ServerError(APIError):
    status_code = 500


class UnavailableError(APIError):
    status_code = 503


def user_exception_handler(request, exc: APIError):
    return response(
        http_status=exc.status_code,
        error=exc.message,
        error_code=exc.error_code,
    )


def global_exception_handler(request, exc: Exception):
    return response(
        http_status=500,
        error='Internal Server Error',
    )


def install_exception_handlers(app):
    # We have 2 exception handlers:
    # - APIError handler - this one handles all errors raised by us, intended
    #   to be displayed to user, which contain the data that will be returned to
    #   the user. These exceptions are expected to happen, and are used for flow
    #   control, therefore they won't appear in Sentry
    # - global exception handler - this one handles all other errors, and will
    #   display the plain `Internal Server Error` to the user. These are the
    #   errors that should never occur, and when they do, they'll get sent to
    #   Sentry so we can act upon them
    app.add_exception_handler(APIError, user_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    # But also, let's remove Starlette's default HTTPException, as in theory,
    # Starlette may raise its own error messages when something goes wrong, and
    # echo them to the user. They won't be in our own standard format, which we
    # don't want to happen
    app.exception_handlers.pop(StarletteHTTPException)
