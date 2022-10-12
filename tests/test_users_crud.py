from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import validate_model
from pytest import mark

from controllers.user_routes import router as client_router
from schemas.project_errors import ProjectErrors
from server.database_test import DataBaseTest

app = FastAPI()
app.include_router(client_router, tags=["user"], prefix="/user")


@app.on_event("startup")
async def startup_db_client():
    app.database = DataBaseTest()
    await app.database.connect_db()


@app.on_event("shutdown")
async def shutdown_db_client():
    await app.database.disconnect_db()


@mark.asyncio
async def test_create_user():
    with TestClient(app) as client:
        response = client.post(
            "/user/", json={"name": "Bruna", "email": "teste@gmail.com", "pwd": "265"}
        )
        assert response.status_code == 201

        body = response.json()
        assert body.get("name") == "Bruna"
        assert body.get("email") == "teste@gmail.com"
        assert body.get("pwd") == "**********"
        assert "_id" in body


@mark.asyncio
async def test_create_user_missing_email():
    with TestClient(app) as client:
        response = client.post("/user/", json={"name": "Bruno", "pwd": "365"})
        assert response.status_code == 422


@mark.asyncio
async def test_create_user_missing_password():
    with TestClient(app) as client:
        response = client.post(
            "/user/", json={"name": "Bruno", "email": "testef@gmail.com"}
        )
        assert response.status_code == 422


@mark.asyncio
async def test_create_user_missing_name():
    with TestClient(app) as client:
        response = client.post(
            "/user/", json={"email": "testef@gmail.com", "pwd": "365"}
        )
        assert response.status_code == 422


@mark.asyncio
async def test_get_user():
    with TestClient(app) as client:
        new_user = client.post(
            "/user/", json={"name": "Joao", "email": "teste2@gmail.com", "pwd": "165"}
        )
        new_user = new_user.json()
        get_user_response = client.get("/user/" + new_user.get("_id"))
        assert get_user_response.status_code == 200
        assert get_user_response.json() == new_user


@mark.asyncio
async def test_get_user_unexisting():
    with TestClient(app) as client:
        get_user_response = client.get("/user/unexisting_id")
        assert get_user_response.status_code == 404


@mark.asyncio
async def test_get_user_emails_by_domain_name():
    with TestClient(app) as client:
        client.post(
            "/user/", json={"name": "Bruna", "email": "teste@hotmail.com", "pwd": "265"}
        )
        client.post(
            "/user/",
            json={"name": "Bruno", "email": "teste2@hotmail.com", "pwd": "465"},
        )
        get_emails_response = client.get("/user/emails/?domain_name=@hotmail.com")
        assert get_emails_response.status_code == 200
        assert (
            validate_model(ProjectErrors, get_emails_response.json())[2] is not None
        )


@mark.asyncio
async def test_update_user():
    with TestClient(app) as client:
        new_user = client.post(
            "/user/", json={"name": "Jorge", "email": "teste3@gmail.com", "pwd": "465"}
        ).json()
        response = client.put("/user/" + new_user.get("_id"), json={"name": "Jorginho"})
        assert response.status_code == 303


@mark.asyncio
async def test_delete_user():
    with TestClient(app) as client:
        new_user = client.post(
            "/user/",
            json={"name": "Jorginho", "email": "teste3@gmail.com", "pwd": "465"},
        ).json()
        delete_user_response = client.delete("/user/" + new_user.get("_id"))
        assert delete_user_response.status_code == 303


@mark.asyncio
async def test_delete_user_unexisting():
    with TestClient(app) as client:
        delete_user_response = client.delete("/user/unexisting_id")
        assert delete_user_response.status_code == 404
