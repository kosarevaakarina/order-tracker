import asyncio
from fastapi import FastAPI, Request
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import ValidationError
from fastapi.responses import JSONResponse
from config.logger import logger
from routers.order_routers import router as order_router
from routers.user_routers import router as user_router
from config.settings import AppSettings
from services.kafka.consumers import consume_orders

app = FastAPI(**AppSettings().model_dump())
app.include_router(order_router, prefix='/v1/api/orders', tags=["orders"])
app.include_router(user_router, prefix='/v1/api/users', tags=["user"])


instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)
request_counter = Counter('app_requests_total', 'Total number of requests', ['endpoint', 'method'])

@app.middleware("http")
async def track_requests(request, call_next):
    response = await call_next(request)
    endpoint = request.url.path
    method = request.method
    request_counter.labels(endpoint=endpoint, method=method).inc()
    return response

if __name__ == "src.main":
    asyncio.create_task(consume_orders())


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.error("Validation error on path %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()[0]['msg']},
    )