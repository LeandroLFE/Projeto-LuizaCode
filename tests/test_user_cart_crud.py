from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import mark

from controllers.cart_routes import router as cart_router
from controllers.user_routes import router as user_router
from server.database_test import DataBaseTest
from utils.generate_fakes import generate_fake_user, generate_fake_cart

app = FastAPI()
app.include_router(cart_router, tags=["cart"], prefix="/cart")
app.include_router(user_router, tags=["user"], prefix="/user")


@app.on_event("startup")
async def startup_db_client():
    app.database = DataBaseTest()
    await app.database.connect_db()


@app.on_event("shutdown")
async def shutdown_db_client():
    await app.database.disconnect_db()


@mark.asyncio
async def test_create_cart():
    with TestClient(app) as client:
        body_client = await generate_fake_user(client)
        response = await generate_fake_cart(client, body_client.json().get("_id"))
        assert response.status_code == 201
        body = response.json()
        assert body.get("price") == 0
        assert not body.get("paid")
        assert body.get("address") == {
            "street": "Rua Z",
            "zipcode": "00000-000",
            "district": "East Zone",
            "city": "GG",
            "state": "SS",
            "is_delivery": True,
        }
        assert "_id" in body


@mark.asyncio
async def test_create_cart_missing_fields():
    with TestClient(app) as client:
        body_client = await generate_fake_user(client)
        response = client.post(
            f"/cart/{body_client.json().get('_id')}", json=[{"authority": ""}]
        )
        assert response.status_code == 422


@mark.asyncio
async def test_get_cart():
    with TestClient(app) as client:
        body_client = await generate_fake_user(client)
        user_id = body_client.json().get("_id")
        response = await generate_fake_cart(client, user_id)
        get_cart_response = client.get("/cart/" + user_id)
        assert get_cart_response.status_code == 200
        assert get_cart_response.json() == response.json()


@mark.asyncio
async def test_get_cart_unexisting():
    with TestClient(app) as client:
        get_cart_response = client.get("/cart/unexisting_id")
        assert get_cart_response.status_code == 404


@mark.asyncio
async def test_update_cart():
    with TestClient(app) as client:
        fake_client = await generate_fake_user(client)
        user_id = fake_client.json().get("_id")
        await generate_fake_cart(client, user_id)
        response = client.put(
            f"/cart/{user_id}",
            json={"authority": "some authority"},
        )
        assert response.status_code == 200
        assert response.json().get("authority") == "some authority"


@mark.asyncio
async def test_delete_cart():
    with TestClient(app) as client:
        user_fake = await generate_fake_user(client)
        user_id = user_fake.json().get("_id")
        await generate_fake_cart(client, user_id)
        delete_cart_response = client.delete("/cart/" + user_id)
        assert delete_cart_response.status_code == 200
        assert delete_cart_response.json().get("status") == "success"
        assert delete_cart_response.json().get("msg") == "Deleted the user cart"


@mark.asyncio
async def test_delete_cart_unexisting():
    with TestClient(app) as client:
        delete_cart_response = client.delete("/cart/unexisting_id")
        assert delete_cart_response.status_code == 404


if __name__ == "__main__":
    test_update_cart()
