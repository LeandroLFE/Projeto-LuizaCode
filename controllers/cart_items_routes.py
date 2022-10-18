from typing import List, Union

from fastapi import APIRouter, Body, HTTPException, Request, status

from models.model_cart_item import (
    create_update_cart_item,
    delete_cart_item,
    get_all_cart_items,
    get_cart_item,
)
from schemas.cart_item import CartItem, CartItemUpdate
from schemas.project_errors import ProjectErrors

router = APIRouter()


@router.put(
    "/",
    response_description="Create a new Cart item",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[CartItem, ProjectErrors],
)
async def route_create_update_cart_item(
    cart_id: str, request: Request, cart_item: CartItemUpdate = Body(...)
):
    return await create_update_cart_item(request.app.database, cart_id, cart_item)


@router.get(
    "/",
    response_description="Return all cart_items from a cart",
    response_model=Union[List[CartItem], ProjectErrors],
)
async def route_get_all_cart_items(cart_id: str, request: Request):
    return await get_all_cart_items(request.app.database, cart_id)


@router.get(
    "/{product_id}",
    response_description="Return an active User cart_item",
    response_model=Union[CartItem, ProjectErrors],
)
async def route_get_a_cart_item(cart_id: str, product_id: str, request: Request):
    if (
        cart_item := await get_cart_item(request.app.database, cart_id, product_id)
    ) is not None:
        return cart_item

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_type": "route_get_user_cart_item",
            "error_msg": f"Cart Item with product ID {product_id} not found",
        },
    )


@router.delete(
    "/{product_id}",
    response_description="Delete a cart item",
    response_model=Union[CartItem, ProjectErrors],
)
async def route_delete_cart_item(
    cart_id: str, product_id: str, request: Request, quantity: int = 1
):
    quantity = 1 if not quantity else quantity
    quantity = 1 if not str(quantity).isdigit() else int(quantity)
    quantity = 1 if quantity < 1 else quantity
    return await delete_cart_item(request.app.database, cart_id, product_id, quantity)
