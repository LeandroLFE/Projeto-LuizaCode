from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import mark

from controllers.product_routes import router as product_router
from server.database_test import DataBaseTest
from utils.generate_fakes import generate_fake_product, generate_fake_products

app = FastAPI()
app.include_router(product_router, tags=["product"], prefix="/products")


@app.on_event("startup")
async def startup_db_client():
    app.database = DataBaseTest()
    await app.database.connect_db()


@app.on_event("shutdown")
async def shutdown_db_client():
    await app.database.disconnect_db()


@mark.asyncio
async def test_create_products():
    with TestClient(app) as client:
        response = await generate_fake_products(client)
        assert response.status_code == 201
        body = response.json()
        assert body[0].get("name") == "Sorvete"
        assert body[0].get("description") == "Doce gelado de morango"
        assert body[0].get("price") == 9.99
        assert "_id" in body[0]


@mark.asyncio
async def test_create_product_missing_name():
    with TestClient(app) as product:
        response = product.post(
            "/products/", json=[{"description": "Doce gelado", "price": 9.99}]
        )
        assert response.status_code == 422


@mark.asyncio
async def test_create_product_missing_description():
    with TestClient(app) as product:
        response = product.post("/products/", json={"name": "Sorvete", "price": 9.99})
        assert response.status_code == 422


@mark.asyncio
async def test_create_product_missing_price():
    with TestClient(app) as product:
        response = product.post(
            "/products/", json={"name": "Sorvete", "description": "Doce gelado"}
        )
        assert response.status_code == 422


@mark.asyncio
async def test_get_product():
    with TestClient(app) as client:
        new_product = await generate_fake_product(client)
        new_product = new_product.json()
        get_product_response = client.get("/products/" + new_product.get("_id"))
        assert get_product_response.status_code == 200
        assert get_product_response.json() == new_product


@mark.asyncio
async def test_get_product_unexisting():
    with TestClient(app) as product:
        get_product_response = product.get("/products/unexisting_id")
        assert get_product_response.status_code == 404


@mark.asyncio
async def test_update_product():
    with TestClient(app) as product:
        new_product = product.post(
            "/products/",
            json={
                "name": "Garrafa vermelha",
                "description": "Recipente de vidro 500ml",
                "price": 19.99,
            },
        ).json()
        response = product.put(
            "/products/" + new_product.get("_id"),
            json={"name": "Garrafa", "descricao": "Recipiente de vidro 500ml vermelho"},
        )
        assert response.status_code == 200
        assert response.json().get("name") == "Garrafa"


@mark.asyncio
async def test_delete_product():
    with TestClient(app) as product:
        new_product = product.post(
            "/products/",
            json={
                "name": "Sabonete",
                "description": "Produto de higiene",
                "price": 7.99,
            },
        ).json()
        delete_product_response = product.delete("/products/" + new_product.get("_id"))
        assert delete_product_response.status_code == 303


@mark.asyncio
async def test_delete_product_unexisting():
    with TestClient(app) as product:
        delete_product_response = product.delete("/products/unexisting_id")
        assert delete_product_response.status_code == 404


if __name__ == "__main__":
    test_update_product()
