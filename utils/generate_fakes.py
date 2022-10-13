async def generate_fake_user(client):
    body_client = client.post(
        "/user/", json={"name": "Bruna", "email": "teste@gmail.com", "pwd": "265"}
    )
    return body_client


async def generate_fake_cart(client, user_id):
    return client.post(
        f"/cart/{user_id}",
        json={
            "price": 0,
            "paid": False,
            "address": {
                "street": "Rua Z",
                "zipcode": "00000-000",
                "district": "East Zone",
                "city": "GG",
                "state": "SS",
                "is_delivery": True,
            },
            "authority": "",
        },
    )


async def generate_fake_products(client):
    return client.post(
        "/products/",
        json=[
            {
                "_id": 10,
                "name": "Sorvete",
                "description": "Doce gelado de morango",
                "price": 9.99,
            },
            {
                "_id": 20,
                "name": "Bolacha",
                "description": "Biscoito doce",
                "price": 4.99,
            },
        ],
    )


async def generate_fake_product(client):
    return client.post(
        "/products/",
        json={"name": "Sabonete", "description": "Produto de higiene", "price": 7.99},
    )


async def generate_fake_cart_item(client, fake_cart, fake_product, quantity=1):
    return client.put(
        "/cart/" + fake_cart.get("_id") + "/item/",
        json={"product": fake_product, "quantity": quantity},
    )
