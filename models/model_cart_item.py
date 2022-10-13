from bson.objectid import ObjectId
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse

from models.model_cart import get_cart_by_id, update_cart
from schemas.cart_item import CartItemUpdate

router = APIRouter()


async def create_update_cart_item(
    database, cart_id: str, cart_item: CartItemUpdate = Body(...)
):
    try:
        cart = await get_cart_by_id(database, cart_id)
        if cart is None:
            return {
                "error_type": "create_update_cart_item",
                "error_msg": "Unknown cart",
            }
    except Exception:
        return {"error_type": "create_update_cart_item", "error_msg": "Unknown cart"}
    else:
        try:
            cart_item = jsonable_encoder(cart_item)
            _product = cart_item["product"]
            _quantity = cart_item["quantity"]

            _quantity = 1 if not _quantity else _quantity
            _quantity = 1 if not str(_quantity).isdigit() else int(_quantity)
            _quantity = 1 if _quantity < 1 else _quantity

            if (
                cart_item_to_update := await get_cart_item_by_product_id(
                    database, _product.get("_id")
                )
            ) is not None:
                if (
                    await update_cart(
                        database,
                        cart.get("user").get("_id"),
                        {
                            "price": cart.get("price")
                            + round(_product.get("price") * _quantity, 2),
                            "items_quantity": cart.get("items_quantity") + _quantity,
                        },
                    )
                ) is not None:
                    aux_item_quantity = cart_item_to_update.get("quantity") + _quantity
                    aux_price = round(
                        cart_item_to_update.get("product").get("price")
                        * aux_item_quantity,
                        2,
                    )
                    return await update_cart_item_quantity_price(
                        database, _product.get("_id"), aux_item_quantity, aux_price
                    )
                return {
                    "error_type": "create_update_cart_item",
                    "error_msg": "Update cart error. Contact the admnistrator",
                }

            aux_price = round(_product.get("price") * _quantity, 2)
            new_cart_item = await database.cart_items_collection.insert_one(
                {
                    "cart": cart,
                    "product": _product,
                    "quantity": _quantity,
                    "item_price": aux_price,
                }
            )
            if new_cart_item is None:
                return {
                    "error_type": "create_update_cart_item",
                    "error_msg": "Insert update error. Contact the admnistrator",
                }
            if (
                await update_cart(
                    database,
                    cart.get("user").get("_id"),
                    {
                        "price": cart.get("price")
                        + round(_product.get("price") * _quantity, 2),
                        "items_quantity": cart.get("items_quantity") + _quantity,
                    },
                )
            ) is not None:
                return await get_cart_item_by_id(database, new_cart_item.inserted_id)

            return {
                "error_type": "create_update_cart_item",
                "error_msg": "Update cart error. Contact the admnistrator",
            }
        except Exception:
            return {
                "error_type": "create_update_cart_item",
                "error_msg": "Insert update error. Contact the admnistrator",
            }


async def get_all_cart_items(database, cart_id: str | ObjectId):
    try:
        if ObjectId.is_valid(cart_id):
            cart_item = database.cart_items_collection.find(
                {"$or": [{"cart._id": cart_id}, {"cart._id": ObjectId(cart_id)}]}
            )
            return await cart_item.to_list(length=100)

        cart_item = database.cart_items_collection.find({"cart._id": cart_id})
        return await cart_item.to_list(length=100)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart is empty",
        )


async def get_cart_item_by_id(database, cart_item_id: str | ObjectId):
    if ObjectId.is_valid(cart_item_id):
        if (
            cart_item := await database.cart_items_collection.find_one(
                {"$or": [{"_id": cart_item_id}, {"_id": ObjectId(cart_item_id)}]}
            )
        ) is not None:
            return cart_item
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item with ID {cart_item_id} not found",
        )
    if (
        cart_item := await database.cart_items_collection.find_one(
            {"_id": cart_item_id}
        )
    ) is not None:
        return cart_item
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Cart item with ID {cart_item_id} not found",
    )


async def get_cart_item(database, cart_id: str, product_id: str):
    try:
        cart = await get_cart_by_id(database, cart_id)
        if cart is None:
            return {
                "error_type": "create_update_cart_item",
                "error_msg": "Unknown cart",
            }
    except Exception:
        return {"error_type": "create_update_cart_item", "error_msg": "Unknown cart"}
    else:
        return await get_cart_item_by_product_id(database, product_id)


async def get_cart_item_by_product_id(database, product_id: str):
    try:
        if ObjectId.is_valid(product_id):
            if (
                cart_item := await database.cart_items_collection.find_one(
                    {
                        "$or": [
                            {"product._id": product_id},
                            {"product._id": ObjectId(product_id)},
                        ]
                    }
                )
            ) is not None:
                return cart_item
        if (
            cart_item := await database.cart_items_collection.find_one(
                {"product._id": product_id}
            )
        ) is not None:
            return cart_item

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item with product ID {product_id} not found",
        )


async def update_cart_item_quantity_price(
    database, product_id, new_quantity, new_item_price
):
    try:
        update_result = await database.cart_items_collection.update_one(
            {"product._id": product_id},
            {"$set": {"quantity": new_quantity, "item_price": new_item_price}},
        )

        if update_result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_type": "update_user",
                    "error_msg": f"User with product id {product_id} not found",
                },
            )
        if (
            cart_item := await get_cart_item_by_product_id(database, product_id)
        ) is not None:
            return cart_item

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_type": "update_user",
                "error_msg": f"User with product id {product_id} not found",
            },
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_type": "update_user",
                "error_msg": f"User with product id {product_id} not found",
            },
        )


async def delete_cart_item(database, cart_id: str, product_id: str, quantity=1):
    try:
        cart = await get_cart_by_id(database, cart_id)
        if cart is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error_type": "delete_cart_item", "error_msg": "Unknown cart"},
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_type": "delete_cart_item", "error_msg": "Unknown cart"},
        )
    else:
        try:
            _quantity = quantity
            if (
                cart_item_to_delete := await get_cart_item_by_product_id(
                    database, product_id
                )
            ) is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error_type": "get_cart_by_id",
                        "error_msg": "No cart_item to delete",
                    },
                )
            _product_price = cart_item_to_delete.get("product").get("price")
            _quantity = (
                _quantity
                if cart_item_to_delete.get("quantity") >= _quantity
                else cart_item_to_delete.get("quantity")
            )
            aux_item_quantity = cart_item_to_delete.get("quantity") - _quantity
            aux_item_price = round(_product_price * aux_item_quantity, 2)
            if aux_item_quantity >= 1:
                _new_cart_price = cart.get("price") - round(
                    _product_price * _quantity, 2
                )
                _new_cart_price = 0 if _new_cart_price < 0 else _new_cart_price
                if (
                    await update_cart(
                        database,
                        cart.get("user").get("_id"),
                        {
                            "price": _new_cart_price,
                            "items_quantity": cart.get("items_quantity") - _quantity
                            if cart.get("items_quantity") - _quantity >= 0
                            else 0,
                        },
                    )
                ) is not None:
                    return await update_cart_item_quantity_price(
                        database, product_id, aux_item_quantity, aux_item_price
                    )

            deleted_cart_item = await database.cart_items_collection.delete_one(
                {"product._id": product_id}
            )
            if deleted_cart_item.deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error_type": "delete_cart_item",
                        "error_msg": "Delete error. Contact the administrator",
                    },
                )
            _new_cart_price = cart.get("price") - round(_product_price * _quantity, 2)
            _new_cart_price = 0 if _new_cart_price < 0 else _new_cart_price
            if (
                await update_cart(
                    database,
                    cart.get("user").get("_id"),
                    {
                        "price": _new_cart_price,
                        "items_quantity": cart.get("items_quantity") - _quantity
                        if cart.get("items_quantity") - _quantity >= 0
                        else 0,
                    },
                )
            ) is not None:
                return RedirectResponse(
                    f"/cart/{cart.get('user').get('_id')}",
                    status_code=status.HTTP_303_SEE_OTHER,
                )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_type": "delete_cart_item",
                    "error_msg": "Update cart error. Contact the administrator",
                },
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_type": "delete_cart_item",
                    "error_msg": "Update cart error. Contact the administrator",
                },
            )
