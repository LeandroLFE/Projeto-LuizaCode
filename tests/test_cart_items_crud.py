from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pytest import mark

from controllers.user_routes import router as user_router, Request, status
from controllers.product_routes import router as product_router
from controllers.cart_items_routes import router as cart_items_router
from controllers.cart_routes import router as cart_router
from project_logs.logging import set_logging
from server.database_test import DataBaseTest
from utils.generate_fakes import (
    generate_fake_cart_item,
    generate_fake_products,
    generate_fake_user,
    generate_fake_cart,
)

app = FastAPI()
app.include_router(user_router, tags=["user"], prefix="/user")
app.include_router(product_router, tags=["products"], prefix="/products")
app.include_router(cart_router, tags=["cart"], prefix="/cart")
app.include_router(cart_items_router, tags=["cart_item"], prefix="/cart/{cart_id}/item")


@app.on_event("startup")
async def startup_db_client():
    app.database = DataBaseTest()
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


@mark.asyncio
async def test_create_update_cart_item():
    with TestClient(app) as client:
        body_client = await generate_fake_user(client)
        fake_products = await generate_fake_products(client)
        user_id = body_client.json().get("_id")
        fake_cart = await generate_fake_cart(client, user_id)
        quantity = 1
        response = await generate_fake_cart_item(
            client, fake_cart.json(), fake_products.json()[0], quantity
        )
        get_cart_response = client.get("/cart/" + user_id)
        assert response.status_code == 201
        body = response.json()
        assert body.get("cart").get("_id") == fake_cart.json().get("_id")
        assert body.get("cart").get("price") == 0
        assert body.get("product").get("price") == 9.99
        assert get_cart_response.json().get("price") == 9.99 * quantity


@mark.asyncio
async def test_create_update_cart_item_with_more_quantity():
    with TestClient(app) as client:
        body_client = await generate_fake_user(client)
        fake_products = await generate_fake_products(client)
        user_id = body_client.json().get("_id")
        fake_cart = await generate_fake_cart(client, user_id)
        quantity = 20
        response = await generate_fake_cart_item(
            client, fake_cart.json(), fake_products.json()[0], quantity
        )
        get_cart_response = client.get("/cart/" + user_id)
        assert response.status_code == 201
        body = response.json()
        assert body.get("cart").get("_id") == fake_cart.json().get("_id")
        assert body.get("cart").get("price") == 0
        assert body.get("product").get("price") == 9.99
        assert get_cart_response.json().get("price") == 9.99 * quantity


@mark.asyncio
async def test_create_update_cart_item_missing_fields():
    with TestClient(app) as client:
        body_client = await generate_fake_user(client)
        fake_products = await generate_fake_products(client)
        user_id = body_client.json().get("_id")
        fake_cart = await generate_fake_cart(client, user_id)
        quantity = 1
        await generate_fake_cart_item(
            client, fake_cart.json(), fake_products.json()[0], quantity
        )
        response = client.put(
            f"/cart/{body_client.json().get('_id')}/item/",
            json={
                "cart": fake_cart.json().get("_id"),
                "product": {
                    "description": "Doce gelado de morango",
                    "price": 9.99,
                }
            },
        )
        assert response.status_code == 422


@mark.asyncio
async def test_get_cart_item():
    with TestClient(app) as client:
        body_client = await generate_fake_user(client)
        fake_products = await generate_fake_products(client)
        user_id = body_client.json().get("_id")
        first_product_id = fake_products.json()[0].get("_id")
        fake_cart = await generate_fake_cart(client, user_id)
        await generate_fake_cart_item(client, fake_cart.json(), fake_products.json()[0])
        get_cart_item_response = client.get(
            "/cart/" + fake_cart.json().get("_id") + "/item/" + first_product_id + "/"
        )
        assert get_cart_item_response.status_code == 200
        assert get_cart_item_response.json().get("cart") == fake_cart.json()
        assert get_cart_item_response.json().get("product") == fake_products.json()[0]


@mark.asyncio
async def test_get_cart_unexisting():
    with TestClient(app) as client:
        get_cart_response = client.get("/cart/unexisting_id")
        assert get_cart_response.status_code == 404


@mark.asyncio
async def test_delete_cart_item():
    with TestClient(app) as client:
        body_client = await generate_fake_user(client)
        fake_products = await generate_fake_products(client)
        user_id = body_client.json().get("_id")
        first_product_id = fake_products.json()[0].get("_id")
        fake_cart = await generate_fake_cart(client, user_id)
        await generate_fake_cart_item(client, fake_cart.json(), fake_products.json()[0])
        delete_cart_item_response = client.delete(
            f"""/cart/{fake_cart.json().get("_id")}/item/{first_product_id}"""
        )
        assert delete_cart_item_response.status_code == 303


@mark.asyncio
async def test_delete_cart_item_with_more_quantity():
    with TestClient(app) as client:
        body_client = await generate_fake_user(client)
        fake_products = await generate_fake_products(client)
        user_id = body_client.json().get("_id")
        first_product_id = fake_products.json()[0].get("_id")
        fake_cart = await generate_fake_cart(client, user_id)
        await generate_fake_cart_item(
            client, fake_cart.json(), fake_products.json()[0], 4
        )
        delete_cart_item_response = client.delete(
            f"""/cart/{fake_cart.json().get("_id")}/item/{first_product_id}"""
        )
        assert delete_cart_item_response.status_code == 200


@mark.asyncio
async def test_delete_cart_item_unexisting():
    with TestClient(app) as client:
        delete_cart_response = client.delete("/cart/unexisting_id/item/10")
        assert delete_cart_response.status_code == 404


@mark.asyncio
async def test_delete_user_cascade():
    with TestClient(app) as client:
        body_client = await generate_fake_user(client)
        fake_products = await generate_fake_products(client)
        user_id = body_client.json().get("_id")
        fake_cart = await generate_fake_cart(client, user_id)
        await generate_fake_cart_item(
            client, fake_cart.json(), fake_products.json()[0], 4
        )
        delete_user_response = client.delete("/user/" + user_id)
        assert delete_user_response.status_code == 303
        get_user_response = client.get("/user/" + user_id)
        assert get_user_response.status_code == 404
        get_cart_response = client.get("/cart/" + user_id)
        assert get_cart_response.status_code == 404
        get_cart_item_response = client.get("/cart/" + fake_cart.json().get("_id"))
        assert get_cart_item_response.status_code == 404


@mark.asyncio
async def test_delete_cart_cascade():
    with TestClient(app) as client:
        body_client = await generate_fake_user(client)
        fake_products = await generate_fake_products(client)
        user_id = body_client.json().get("_id")
        fake_cart = await generate_fake_cart(client, user_id)
        await generate_fake_cart_item(
            client, fake_cart.json(), fake_products.json()[0], 4
        )
        delete_cart_response = client.delete("/cart/" + user_id)
        assert delete_cart_response.status_code == 200
        assert delete_cart_response.json().get("status") == "success"
        assert delete_cart_response.json().get("msg") == "Deleted the user cart"
        get_cart_response = client.get("/cart/" + user_id)
        assert get_cart_response.status_code == 404
        get_cart_item_response = client.get("/cart/" + fake_cart.json().get("_id"))
        assert get_cart_item_response.status_code == 404


if __name__ == "__main__":
    pass
