from typing import List, Union

from fastapi import APIRouter, Body, Request

from models.model_address import add_address, delete_Address, list_address
from schemas.address import Address
from schemas.project_errors import ProjectErrors

router = APIRouter()


@router.put("/", response_description="Add a new Address", response_model=ProjectErrors)
async def route_add_address(
    user_id: str,
    request: Request,
    address: Address = Body(...),
):
    return await add_address(request.app.database, user_id, address)


@router.get(
    "/",
    response_description="List address",
    response_model=Union[List[Address], ProjectErrors],
)
async def route_list_address(
    user_id: str,
    request: Request,
):
    return await list_address(request.app.database, user_id)


@router.delete(
    "/", response_description="Remove an Address", response_model=ProjectErrors
)
async def route_delete_address(
    user_id: str,
    request: Request,
    address: Address = Body(...),
):
    return await delete_Address(request.app.database, user_id, address)
