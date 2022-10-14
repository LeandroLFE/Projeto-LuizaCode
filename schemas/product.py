from typing import Optional, Union
from uuid import uuid4

from bson.objectid import ObjectId
from pydantic import BaseModel, Field

from utils.pydantic_objectid import PyObjectId


class Product(BaseModel):
    """
    Product data class
    """

    id: Union[str, PyObjectId] = Field(default_factory=uuid4, alias="_id")
    name: str = Field(...)
    description: str = Field(...)
    price: float = Field(...)

    class Config:
        allow_population_by_field_name = True
        smart_union = True
        json_encoders = {ObjectId: str}


class ProductUpdate(BaseModel):
    """
    Class for Product update
    """

    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
