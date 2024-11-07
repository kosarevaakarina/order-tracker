import asyncio
from fastapi import FastAPI, Request
from pydantic import ValidationError
from fastapi.responses import JSONResponse
from config.logger import logger
from routers.order_routers import router as order_router
from routers.user_routers import router as user_router
from config.settings import AppSettings
from services.kafka.consumers import consume_notification

app = FastAPI(**AppSettings().model_dump())
app.include_router(order_router, prefix='/v1/api/orders', tags=["orders"])
app.include_router(user_router, prefix='/v1/api/users', tags=["user"])

asyncio.create_task(consume_notification())


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.error("Validation error on path %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()[0]['msg']},
    )