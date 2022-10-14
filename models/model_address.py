from typing import List, Union

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from models.model_user import get_user_by_id
from schemas.address import Address
from schemas.project_errors import ProjectErrors
from schemas.user import User


async def add_address(database, user_id: str, address: Address) -> ProjectErrors:
    try:
        address = jsonable_encoder(address)
        user = await get_user_by_id(database, user_id)

        if len(list(filter(lambda a: a == address, user["address"]))) > 0:
            return {
                "error_type": "add_address",
                "error_msg": "This user has this address already. Add another one",
            }

        user["address"].append(address)
        update_result = await database.users_collection.update_one(
            {"_id": user_id}, {"$set": {"address": user["address"]}}
        )
        if update_result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_type": "update_user_add_address",
                    "error_msg": f"User with id {user_id} not found",
                },
            )
        return RedirectResponse(
            f"/user/{user_id}/address", status_code=status.HTTP_303_SEE_OTHER
        )

    except Exception as e:
        print("add_address.error", e)
        return {
            "error_type": "add_address",
            "error_msg": "It was not possible to add a new address. Contact the administrator",
        }


async def list_address(database, user_id: str) -> Union[List[Address], ProjectErrors]:
    user = await get_user_by_id(database, user_id)
    try:
        User.validate(user)
        return user["address"]

    except ValidationError:
        return user


async def delete_Address(database, user_id: str, address: Address) -> ProjectErrors:
    try:
        address = jsonable_encoder(address)
        user = await get_user_by_id(database, user_id)

        try:
            User.validate(user)

        except ValidationError:
            return user

        else:
            user["address"] = list(filter(lambda a: a != address, user["address"]))
            update_result = await database.users_collection.update_one(
                {"_id": user_id}, {"$set": {"address": user["address"]}}
            )
            if update_result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error_type": "update_user_delete_address",
                        "error_msg": f"User with id {user_id} not found",
                    },
                )
            return RedirectResponse(
                f"/user/{user_id}/address", status_code=status.HTTP_303_SEE_OTHER
            )

    except Exception as e:
        print("add_address.error", e)
        return {
            "error_type": "delete_address",
            "error_msg": "It was not possible to delete the address. Contact the administrator",
        }
