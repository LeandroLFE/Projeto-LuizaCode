from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from bson.objectid import ObjectId
from pydantic import BaseModel, Field

from schemas.address import Address
from schemas.user import User
from utils.pydantic_objectid import PyObjectId


class Cart(BaseModel):
    """
    Class for a Cart of the User
    """

    id: PyObjectId | str = Field(default_factory=uuid4, alias="_id")
    user: User
    price: Decimal = Field(max_digits=10, decimal_places=2)
    paid: bool = Field(default=False)
    create: datetime = Field(default=datetime.now())
    address: Address
    authority: str | None = Field(max_length=100)
    items_quantity: int = 0

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        smart_union = True
        json_encoders = {ObjectId: str}


class CartInsert(BaseModel):
    """
    Class for insert a new User cart
    """

    price: Decimal = Field(max_digits=10, decimal_places=2)
    paid: bool = Field(default=False)
    create: datetime = Field(default=datetime.now())
    address: Address
    authority: str | None = Field(max_length=100)
    items_quantity: int = 0


class CartUpdate(BaseModel):
    """
    Class for update Cart
    """

    price: Decimal | None
    paid: bool | None
    address: Address | None
    authority: str | None
    items_quantity: int | None
