from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from uvicorn import run as uvicorn_run

from controllers.address_routes import router as address_router
from controllers.cart_items_routes import router as cart_items_router
from controllers.cart_routes import router as cart_router
from controllers.product_routes import router as product_router
from controllers.user_routes import router as user_router
from project_logs.logging import set_logging
from server.database import DataBase

app = FastAPI()


@app.on_event("startup")
async def startup_db_client():
    app.database = DataBase()
    await app.database.connect_db()


@app.on_event("shutdown")
async def shutdown_db_client():
    await app.database.disconnect_db()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    project_errors = []
    project_error = {}
    error_log = set_logging("errors")
    for error in exc.errors():
        project_error["error_loc"] = error["loc"]
        project_error["error_type"] = error["type"]
        project_error["error_msg"] = error["msg"]
        project_errors.append(project_error)
        error_log.error(project_error)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(project_errors),
    )


app.include_router(user_router, tags=["user"], prefix="/user")
app.include_router(product_router, tags=["products"], prefix="/products")
app.include_router(address_router, tags=["address"], prefix="/user/{user_id}/address")
app.include_router(cart_router, tags=["cart"], prefix="/cart")
app.include_router(cart_items_router, tags=["cart_item"], prefix="/cart/{cart_id}/item")

if __name__ == "__main__":
    uvicorn_run("server.api:app", host="0.0.0.0", port=8000, reload=True)
