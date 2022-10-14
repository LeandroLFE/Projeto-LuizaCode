from bson.objectid import ObjectId
from fastapi import status
from fastapi.exceptions import HTTPException


async def delete_all_cart_items(database, cart_id: str):
    try:
        deleted_cart_item = await database.cart_items_collection.delete_many(
            {"cart._id": cart_id}
        )
        return deleted_cart_item.deleted_count
    except Exception:
        return {
            "error_type": "delete_cart_item",
            "error_msg": "Delete error. Contact the administrator",
        }


async def delete_a_cart(database, user_id):
    try:
        if ObjectId.is_valid(user_id):
            deleted_cart = await database.cart_collection.delete_one(
                {
                    "$or": [
                        {"$and": [{"user._id": user_id}, {"paid": False}]},
                        {"$and": [{"user._id": ObjectId(user_id)}, {"paid": False}]},
                    ]
                }
            )
            if deleted_cart.deleted_count == 1:
                return {"status": "success", "msg": "Deleted the user cart"}
            return {
                "error_type": "delete_cart_item",
                "error_msg": "Delete error. Contact the administrator",
            }

        deleted_cart = await database.cart_collection.delete_one(
            {"$and": [{"user._id": user_id}, {"paid": False}]}
        )
        if deleted_cart.deleted_count == 1:
            return {"status": "success", "msg": "Deleted the user cart"}
        return {
            "error_type": "delete_cart_item",
            "error_msg": "Delete error. Contact the administrator",
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart with ID {user_id} not found",
        )


async def get_a_cart_by_user_id(database, user_id: str):
    try:
        if (
            cart := await database.cart_collection.find_one(
                {"$and": [{"user._id": user_id}, {"paid": False}]}
            )
        ) is not None:
            return cart
    except Exception:
        return {
            "error_type": "get_a_user_cart",
            "error_msg": f"Cart for the user {user_id} not found",
        }


async def get_a_cart_by_cart_id(database, cart_id: str):
    try:
        if (
            cart := await database.cart_collection.find_one(
                {"$and": [{"_id": cart_id}, {"paid": False}]}
            )
        ) is not None:
            return cart
    except Exception:
        return {
            "error_type": "get_a_user_cart",
            "error_msg": f"Cart for the user {cart_id} not found",
        }


async def cascade_delete(database, id: str, mode="user"):
    if (cart := await get_a_cart_by_user_id(database, id)) is None:
        return None
    if mode == "user":
        await delete_all_cart_items(database, cart.get("_id"))
        return await delete_a_cart(database, id)
    else:
        cart = await get_a_cart_by_cart_id(database, id)
        await delete_all_cart_items(database, cart.get("_id"))
        return await delete_a_cart(database, cart.get("user").get("_id"))
