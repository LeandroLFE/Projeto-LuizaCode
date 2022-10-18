from typing import List, Optional, Union

from fastapi import APIRouter, Body, Request, status

from models.model_user import (
    create_user,
    delete_user,
    get_emails_by_domain,
    get_user_by_id,
    get_users_by_name,
    list_users,
    update_user,
)
from schemas.project_errors import ProjectErrors
from schemas.user import EmailsList, User, UserUpdate

router = APIRouter()


@router.post(
    "/",
    response_description="Create a new User",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[User, ProjectErrors],
)
async def route_create_user(
    request: Request, status_code=status.HTTP_201_CREATED, user: User = Body(...)
):
    return await create_user(request.app.database, user)


@router.get(
    "/",
    response_description="List users",
    response_model=Union[List[User], ProjectErrors],
)
async def route_list_users(request: Request, page: Optional[int] = None):
    return await list_users(request.app.database, page)


@router.get(
    "/{user_id}",
    response_description="Return an User by Id",
    response_model=Union[User, ProjectErrors],
)
async def route_get_user_by_id(user_id: str, request: Request):
    return await get_user_by_id(request.app.database, user_id)


@router.get(
    "/name/{user_name}",
    response_description="Return an User by name",
    response_model=Union[List[User], ProjectErrors],
)
async def route_get_users_by_name(user_name: str, request: Request):
    return await get_users_by_name(request.app.database, user_name)


@router.get(
    "/emails/",
    response_description="Return number of emails by domain name",
    response_model=Union[EmailsList, ProjectErrors],
)
async def route_get_emails_by_domain(domain_name: str, request: Request):
    return await get_emails_by_domain(request.app.database, domain_name)


@router.put(
    "/{user_id}", response_description="Update an User", response_model=ProjectErrors
)
async def route_update_user(
    user_id: str, request: Request, user: UserUpdate = Body(...)
):
    return await update_user(request.app.database, user_id, user)


@router.delete("/{user_id}", response_description="Delete an User")
async def route_delete_user(user_id: str, request: Request):
    return await delete_user(request.app.database, user_id)
