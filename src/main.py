from fastapi import FastAPI
from routers.order_routers import router as order_router
from routers.user_routers import router as user_router
from config.settings import AppSettings


app = FastAPI(**AppSettings().model_dump())
app.include_router(order_router, prefix='/v1/api/orders', tags=["orders"])
app.include_router(user_router, prefix='/v1/api/users', tags=["user"])


