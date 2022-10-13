from re import match
from typing import List

from fastapi import APIRouter, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse

from schemas.project_errors import ProjectErrors
from schemas.user import EmailsList, User, UserUpdate
from utils.cascade_delete import cascade_delete
from utils.validade_unique_email import validade_unique_email

router = APIRouter()


async def create_user(database, user):
    try:
        user = jsonable_encoder(user)
        list_of_users = await list_users(database)
        if not await validade_unique_email(list_of_users, user["email"]):
            return {
                "error_type": "create_user",
                "error_msg": "It was not possible to create a new user. Contact the administrator",
            }
        new_user = await database.users_collection.insert_one(user)
        created_user = await database.users_collection.find_one(
            {"_id": new_user.inserted_id}
        )
        return created_user

    except Exception as e:
        print("create_user.error", e)
        return {
            "error_type": "create_user",
            "error_msg": "It was not possible to create a new user. Contact the administrator",
        }


async def list_users(database, page: int | None = None) -> List[User] | ProjectErrors:
    if page is None:
        try:
            users = database.users_collection.find()
            users_list = await users.to_list(length=100)
            return users_list

        except Exception as e:
            print("list_users.error", e)
            return {
                "error_type": "list_users",
                "error_msg": "It was not possible to list users. Contact the administrator",
            }

    try:
        limit_per_page = 2
        page = 1 if page < 1 else page
        skip_page = limit_per_page * (page - 1) if page > 0 else 0
        users = database.users_collection.find(skip=skip_page, limit=limit_per_page)
        users_list = await users.to_list(length=limit_per_page)
        return users_list

    except Exception as e:
        print("list_users_by_page.error", e)
        return {
            "error_type": "list_users_by_page",
            "error_msg": "It was not possible to list users by this page. Contact the administrator",
        }


async def get_user_by_id(database, user_id: str) -> User | ProjectErrors:
    user = await database.users_collection.find_one({"_id": user_id})
    if user is not None:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_type": "get_user_by_id",
            "error_msg": f"User with ID {user_id} not found",
        },
    )


async def get_users_by_name(database, user_name: str) -> List[User] | ProjectErrors:
    try:
        user = database.users_collection.find({"name": user_name})
        user = await user.to_list(length=100)
        return user

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_type": "get_user_by_name",
                "error_msg": f"User with name {user_name} not found",
            },
        )


async def update_user(
    database, user_id: str, user: UserUpdate = Body(...)
) -> ProjectErrors:
    user = {k: v for k, v in user.dict().items() if v is not None}

    if len(user) >= 1:
        update_result = await database.users_collection.update_one(
            {"_id": user_id}, {"$set": user}
        )

        if update_result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_type": "update_user",
                    "error_msg": f"User with id {user_id} not found",
                },
            )

    if await database.users_collection.find_one({"_id": user_id}) is not None:
        return RedirectResponse(
            f"/user/{user_id}/", status_code=status.HTTP_303_SEE_OTHER
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_type": "update_user",
            "error_msg": f"User with id {user_id} not found",
        },
    )


async def delete_user(database, user_id: str):
    try:
        delete_result = await database.users_collection.delete_one({"_id": user_id})
        if delete_result.deleted_count == 1:
            await cascade_delete(database, user_id)
            return RedirectResponse("/user/", status_code=status.HTTP_303_SEE_OTHER)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_type": "delete_user",
                "error_msg": f"User with id {user_id} not found",
            },
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_type": "delete_user",
                "error_msg": "Error to delete user, contact the administrator",
            },
        )


async def get_emails_by_domain(database, domain: str) -> EmailsList | ProjectErrors:
    try:
        if not match(r"^@[a-zA-Z]+\.[a-zA-Z]{1,3}$", domain):
            return {
                "error_type": "get_emails_by_domain",
                "error_msg": "Invalid domain",
            }
        emails_list = database.users_collection.find(
            {"email": {"$regex": f"{domain}$", "$options": "i"}},
            {"_id": 0, "email": 1},
        )
        emails_list = await emails_list.to_list(length=100)
        emails_list = [v["email"] for v in emails_list]
        return {
            "emails_count": len(emails_list),
            "emails_list": emails_list,
        }

    except Exception as e:
        print("get_emails_by_domain.error", e)
        return {
            "error_type": "get_emails_by_domain",
            "error_msg": "Get emails by domain failured. Contact the administrator",
        }
