from os import getenv

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


class DataBaseTest:
    client: AsyncIOMotorClient = None
    users_collection = None
    address_collection = None
    product_collection = None
    cart_collection = None
    cart_items_collection = None
    database_uri = None

    def __init__(self) -> None:
        load_dotenv()
        self.database_uri = getenv("DATABASE_URI")

    def connect_db(self):
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


class ContextDb:
    def __init__(self):
        self.db = DataBaseTest()
        self.db.connect_db()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.client.close()


async def get_db():
    with ContextDb() as db:
        yield db


async def drop_databases_to_test():
    with ContextDb() as db:
        await db.disconnect_db()
