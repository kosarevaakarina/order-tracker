from fastapi import FastAPI
from api.order_api import order_router
from config.settings import AppSettings


app = FastAPI(**AppSettings().model_dump())
app.include_router(order_router, prefix='/v1/api/orders', tags=["orders"])


