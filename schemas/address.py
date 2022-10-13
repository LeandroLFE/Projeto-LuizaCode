from pydantic import BaseModel, Field


class Address(BaseModel):
    """
    Class for Address
    """

    street: str = Field(...)
    zipcode: str = Field(...)
    district: str = Field(...)
    city: str = Field(...)
    state: str = Field(...)
    is_delivery: bool = Field(default=True)

    def __str__(self) -> str:
        return f"""{self.street} - {self.zipcode} - {self.district} - {self.city} - {self.state}"""
