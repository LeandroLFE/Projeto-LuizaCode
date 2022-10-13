from pydantic import BaseModel, Field


class ProjectErrors(BaseModel):
    """
    Class for Errors
    """

    error_type: str = Field(...)
    error_msg: str = Field(...)
