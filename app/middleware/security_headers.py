from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Receive, Scope, Send


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Content-Type-Options"] = "nosniff"
                headers["X-Frame-Options"] = "DENY"
                headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
                headers["Content-Security-Policy"] = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' https://accounts.google.com; "
                    "style-src 'self' 'unsafe-inline'; "
                    "frame-src https://accounts.google.com; "
                    "connect-src 'self'; "
                    "img-src 'self' data:; "
                    "object-src 'none'"
                )
            await self.app(scope, receive, send_wrapper)

        await self.app(scope, receive, send_wrapper)
