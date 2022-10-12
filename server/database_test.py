from os import getenv

from motor.motor_asyncio import AsyncIOMotorClient


class DataBaseTest:
    client: AsyncIOMotorClient = None
    database_uri = getenv("DATABASE_URI")
    users_collection = None
    address_collection = None
    product_collection = None
    cart_collection = None
    cart_items_collection = None

    async def connect_db(self):
        # conexao mongo, com no máximo 10 conexões async
        self.client = AsyncIOMotorClient(
            self.database_uri,
            maxPoolSize=10,
            minPoolSize=10,
            tls=True,
            tlsAllowInvalidCertificates=True,
        )
        self.users_collection = self.client.shopping_cart_test.users
        self.address_collection = self.client.shopping_cart_test.address
        self.product_collection = self.client.shopping_cart_test.products
        self.cart_collection = self.client.shopping_cart_test.carts
        self.cart_items_collection = self.client.shopping_cart_test.cart_items

    async def disconnect_db(self):
        await self.users_collection.drop()
        await self.address_collection.drop()
        await self.product_collection.drop()
        await self.cart_collection.drop()
        await self.cart_items_collection.drop()
        self.client.close()
