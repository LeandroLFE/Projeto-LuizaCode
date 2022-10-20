from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import mark

from controllers.address_routes import router as address_router
from controllers.user_routes import router as client_router
from server.database import get_db
from server.database_test import drop_databases_to_test, get_db as get_test_db
from utils.generate_fakes import generate_fake_user

app = FastAPI()
app.include_router(client_router, tags=["user"], prefix="/user")
app.include_router(address_router, tags=["address"], prefix="/user/{user_id}/address")

app.dependency_overrides[get_db] = get_test_db


@app.on_event("shutdown")
async def shutdown_db_client():
    await drop_databases_to_test()


@mark.asyncio
async def test_create_address():
    with TestClient(app) as client:
        body_client = await generate_fake_user(client)
        user_id = body_client.json().get("_id")
        response = client.put(
            "/user/" + user_id + "/address/",
            json={
                "street": "Rua X",
                "zipcode": "00000-000",
                "district": "West Zone",
                "city": "GG",
                "state": "HH",
                "is_delivery": True,
            },
        )
        assert response.status_code == 303

        user = client.get(f"/user/{user_id}")
        user = user.json()
        assert user["address"][0].get("street") == "Rua X"
        assert user["address"][0].get("zipcode") == "00000-000"
        assert user["address"][0].get("district") == "West Zone"
        assert user["address"][0].get("city") == "GG"
        assert user["address"][0].get("state") == "HH"
        assert user["address"][0].get("is_delivery") is True


@mark.asyncio
async def test_create_address_missing_street():
    with TestClient(app) as client:
        body_client = await generate_fake_user(client)
        user_id = body_client.json().get("_id")
        response = client.put(
            "/user/" + user_id + "/address/",
            json=[
                {
                    "zipcode": "00000-000",
                    "district": "West Zone",
                    "city": "GG",
                    "state": "HH",
                    "is_delivery": True,
                }
            ],
        )
        assert response.status_code == 422


@mark.asyncio
async def test_get_address_list():
    with TestClient(app) as client:
        new_address = [
            {
                "street": "Rua Z",
                "zipcode": "00000-000",
                "district": "West Zone",
                "city": "GG",
                "state": "HH",
                "is_delivery": True,
            }
        ]
        body_client = client.post(
            "/user/",
            json={
                "name": "Bruna",
                "email": "teste@gmail.com",
                "pwd": "265",
                "address": new_address,
            },
        ).json()
        get_user_response = client.get("/user/" + body_client.get("_id") + "/address")
        assert get_user_response.status_code == 200
        assert get_user_response.json() == new_address


@mark.asyncio
async def test_delete_address():
    with TestClient(app) as client:
        address_json = {
            "street": "Rua ZA",
            "zipcode": "00000-000",
            "district": "West Zone",
            "city": "GG",
            "state": "HH",
            "is_delivery": True,
        }
        body_client = client.post(
            "/user/",
            json={
                "name": "Bruna",
                "email": "teste@gmail.com",
                "pwd": "265",
                "address": [address_json],
            },
        ).json()
        delete_address_response = client.delete(
            "/user/" + body_client.get("_id") + "/address/",
            json=address_json,
        )
        assert delete_address_response.status_code == 303

        user = client.get(f"/user/{body_client.get('_id')}")
        user = user.json()
        assert user["address"] == []


@mark.asyncio
async def test_delete_address_unexisting():
    with TestClient(app) as client:
        delete_address_response = client.delete("/address/unexisting_id")
        assert delete_address_response.status_code == 404


if __name__ == "__main__":
    pass
