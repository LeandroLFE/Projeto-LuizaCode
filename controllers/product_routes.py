from typing import List, Union

from fastapi import APIRouter, Body, Depends, Request, status

from models.model_product import (
    create_products,
    delete_product,
    list_product_by_id,
    list_products,
    update_product,
)
from schemas.product import Product, ProductUpdate
from schemas.project_errors import ProjectErrors
from server.database import get_db

router = APIRouter()


@router.post(
    "/",
    response_description="Create new Products",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[List[Product], Product],
)
async def route_create_products(
    request: Request,
    products: Union[List[Product], Product] = Body(...),
    db: get_db = Depends()
):
    return await create_products(db, products)


@router.get("/", response_description="List all Products", response_model=List[Product])
async def route_list_products(request: Request, db: get_db = Depends()):
    return await list_products(db)


@router.get(
    "/{product_id}",
    response_description="Return a Product by Id",
    response_model=Product,
)
async def route_list_product_by_id(
    product_id: str, request: Request, db: get_db = Depends()
):
    return await list_product_by_id(db, product_id)


@router.put(
    "/{product_id}",
    response_description="Update a product",
    response_model=Union[Product, ProjectErrors],
)
async def route_update_product(
    product_id: str,
    request: Request,
    product: ProductUpdate = Body(...),
    db: get_db = Depends(),
):
    return await update_product(db, product_id, product)


@router.delete("/{product_id}", response_description="Delete a product")
async def route_delete_product(
    product_id: str, request: Request, db: get_db = Depends()
):
    return await delete_product(db, product_id)
