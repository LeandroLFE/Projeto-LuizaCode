from pydantic import BaseModel, Field


class ProjectSuccess(BaseModel):
    """
    Class for Success
    """

    status: str = Field(...)
    msg: str = Field(...)
