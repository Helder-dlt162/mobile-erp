from time import perf_counter
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.db import SessionLocal
from app.models import AuditLog


class RequestAuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id
        started = perf_counter()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-ms"] = f"{(perf_counter() - started) * 1000:.2f}"
        if request.url.path != "/health":
            db = SessionLocal()
            try:
                db.add(AuditLog(request_id=request_id, method=request.method, path=request.url.path, status_code=response.status_code))
                db.commit()
            except Exception:
                db.rollback()
            finally:
                db.close()
        return response
