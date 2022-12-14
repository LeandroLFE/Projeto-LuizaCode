from typing import Union

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status

from models.model_cart import create_cart, delete_cart, get_user_cart, update_cart
from schemas.cart import Cart, CartInsert, CartUpdate
from schemas.project_errors import ProjectErrors
from server.database import get_db

router = APIRouter()


@router.post(
    "/{user_id}",
    response_description="Create a new Cart if there is no active",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[Cart, ProjectErrors],
)
async def route_create_cart(
    user_id: str,
    request: Request,
    cart: CartInsert = Body(...),
    db: get_db = Depends(),
):
    return await create_cart(db, user_id, cart)


@router.get(
    "/{user_id}",
    response_description="Return an active User cart",
    response_model=Union[Cart, ProjectErrors],
)
async def route_get_user_cart(
    user_id: str,
    request: Request,
    db: get_db = Depends(),
):
    if (get_cart := await get_user_cart(db, user_id)) is not None:
        return get_cart

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_type": "route_get_user_cart",
            "error_msg": f"Cart with user ID {user_id} not found",
        },
    )


@router.put(
    "/{user_id}",
    response_description="Update a cart",
    response_model=Union[Cart, ProjectErrors],
)
async def route_update_cart(
    user_id: str,
    request: Request,
    cart: CartUpdate = Body(...),
    db: get_db = Depends(),
):
    if (cart_update := await update_cart(db, user_id, cart)) is not None:
        return cart_update

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error_type": "route_update_cart",
            "error_msg": f"Cart with user ID {user_id} not found",
        },
    )


@router.delete("/{user_id}", response_description="Delete the user cart")
async def route_delete_cart(
    user_id: str,
    request: Request,
    db: get_db = Depends(),
):
    return await delete_cart(db, user_id)
