import logging, time, uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp

logger = logging.getLogger("rag")

class RequestLogginMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        start = time.perf_counter()
        try:
            response = await call_next(request)
            status = response.status_code
        except Exception as e:
            status = 500
            logger.exception("unhandled error", extra={"request_id": request_id})
            raise
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info("req method=%s path=%s status=%s duration_ms=%.2f request_id=%s",
    request.method, request.url.path, status, duration_ms, request_id)
        
        response.headers["X-Request-ID"] = request_id
        return response