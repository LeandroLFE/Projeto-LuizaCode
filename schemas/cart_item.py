from bson.objectid import ObjectId
from pydantic import BaseModel

from schemas.cart import Cart
from schemas.product import Product


class CartItem(BaseModel):
    """
    Class for a Cart Item
    """

    cart: Cart
    product: Product
    quantity: int = 1

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class CartItemUpdate(BaseModel):
    """
    Class for Update a Cart Item
    """

    product: Product
    quantity: int = 1
    item_price: int = 0
