from os import getenv

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from project_logs.logging import set_logging


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
        self.logger = set_logging("info")
        self.logger.info("ENV loaded!")

    async def connect_db(self):
        # conexao mongo, com no máximo 10 conexões async
        self.client = AsyncIOMotorClient(
            self.database_uri,
            maxPoolSize=10,
            minPoolSize=10,
            tls=True,
            tlsAllowInvalidCertificates=True,
        )
        self.users_collection = self.client.shopping_cart.users
        self.address_collection = self.client.shopping_cart.address
        self.product_collection = self.client.shopping_cart.products
        self.cart_collection = self.client.shopping_cart.cart
        self.cart_items_collection = self.client.shopping_cart.cart_items

    async def disconnect_db(self):
        self.client.close()
