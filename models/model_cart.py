from bson.objectid import ObjectId
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError, validate_model

from models.model_user import get_user_by_id
from schemas.cart import Cart, CartUpdate
from schemas.project_errors import ProjectErrors
from utils.cascade_delete import cascade_delete

router = APIRouter()


async def create_cart(database, user_id: str, cart: Cart = Body(...)):
    try:
        cart_user = await get_user_cart(database, user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_type": "get_user_by_id",
                "error_msg": f"Cart of user ID {user_id} not found",
            },
        )
    else:
        if cart_user is not None:
            return cart_user
        try:
            user = await get_user_by_id(database, user_id)
            if user is None:
                return {
                    "error_type": "create_cart",
                    "error_msg": "Insert error. User not found",
                }
            if validate_model(ProjectErrors, user)[2] is None:
                return user
        except ValidationError:
            return {
                "error_type": "create_cart",
                "error_msg": "Insert error. Contact the admninistrator",
            }
        else:
            _cart = jsonable_encoder(cart)
            _cart["user"] = user
            try:
                new_cart = await database.cart_collection.insert_one(_cart)
            except Exception:
                return {
                    "error_type": "create_cart",
                    "error_msg": "Insert error. Contact the admninistrator",
                }
            else:
                created_cart = await get_cart_by_id(database, new_cart.inserted_id)
                return (
                    created_cart
                    if created_cart
                    else {
                        "error_type": "get_cart_by_id",
                        "error_msg": f"Cart of user ID {new_cart.inserted_id} not found",
                    }
                )


async def get_user_cart(database, user_id: str):
    try:
        if (
            user := await database.cart_collection.find_one(
                {"$and": [{"user._id": user_id}, {"paid": False}]}
            )
        ) is not None:
            return user
    except Exception:
        return {
            "error_type": "get_user_cart",
            "error_msg": f"Cart for the user {user_id} not found",
        }


async def get_cart_by_id(database, cart_id: str):
    try:
        if ObjectId.is_valid(cart_id):
            if (
                cart := await database.cart_collection.find_one(
                    {
                        "$or": [
                            {"$and": [{"_id": cart_id}, {"paid": False}]},
                            {"$and": [{"_id": ObjectId(cart_id)}, {"paid": False}]},
                        ]
                    }
                )
            ) is not None:
                return cart
        if (
            cart := await database.cart_collection.find_one(
                {"$and": [{"_id": cart_id}, {"paid": False}]}
            )
        ) is not None:
            return cart
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_type": "get_cart_by_id",
                "error_msg": f"Cart with ID {cart_id} not found",
            },
        )


async def update_cart(database, user_id: str, cart: CartUpdate = Body(...)):
    cart = jsonable_encoder(cart)
    cart = {k: v for k, v in cart.items() if v is not None}

    update_result = await database.cart_collection.update_one(
        {"user._id": user_id}, {"$set": cart}
    )
    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart with ID {user_id} not found",
        )

    if (
        existing_cart := await database.cart_collection.find_one({"user._id": user_id})
    ) is not None:
        return existing_cart

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Cart with ID {user_id} not found",
    )


async def delete_cart(database, user_id: str):
    if (response := await cascade_delete(database, user_id)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart with ID {user_id} not found",
        )
    return response
