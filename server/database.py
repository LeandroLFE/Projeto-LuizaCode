from asyncio import get_event_loop
from os import getenv

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


class DataBase:
    client: AsyncIOMotorClient = None
    database_uri = None
    users_collection = None
    address_collection = None
    product_collection = None
    cart_collection = None
    cart_items_collection = None
    logger = None

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
        self.client.get_io_loop = get_event_loop
        self.users_collection = self.client.shopping_cart.users
        self.address_collection = self.client.shopping_cart.address
        self.product_collection = self.client.shopping_cart.products
        self.cart_collection = self.client.shopping_cart.cart
        self.cart_items_collection = self.client.shopping_cart.cart_items

    def disconnect_db(self):
        self.client.close()


class ContextDb:
    def __init__(self):
        self.db = DataBase()
        self.db.connect_db()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.client.close()


async def get_db():
    with ContextDb() as db:
        yield db
