from typing import List, Optional, Union
from uuid import uuid4

from bson.objectid import ObjectId
from pydantic import BaseModel, Field, SecretStr

from schemas.address import Address
from utils.pydantic_objectid import PyObjectId

email_pattern = r"^([\da-zA-Z]+){3,}@[\da-zA-Z]+\.[a-zA-Z]+(\.[a-zA-Z]+)?$"


class User(BaseModel):
    """
    Class for Users
    """

    id: Union[str, PyObjectId] = Field(default_factory=uuid4, alias="_id")
    name: str = Field(...)
    email: str = Field(regex=email_pattern)
    pwd: SecretStr = Field(...)
    address: List[Address] = []

    class Config:
        allow_population_by_field_name = True
        smart_union = True
        json_encoders = {ObjectId: str}


class UserUpdate(BaseModel):
    """
    Class for update an User
    """

    name: Optional[str]
    email: Optional[str]
    pwd: Optional[str]


class EmailsList(BaseModel):
    """
    Class to show the Emails
    """

    emails_count: int = Field(...)
    emails_list: List[str] = Field(...)
