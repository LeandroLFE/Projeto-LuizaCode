from typing import List

from fastapi import APIRouter, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse

from schemas.product import Product, ProductUpdate

router = APIRouter()


async def create_products(database, products: List[Product] | Product = Body(...)):
    created_products = []
    new_products = products if isinstance(products, list) else [products]
    for product in new_products:
        _product = jsonable_encoder(product)
        try:
            new_product = await database.product_collection.insert_one(_product)
        except Exception as e:
            print("Erro na inserção", e)
        else:
            created_product = await database.product_collection.find_one(
                {"_id": new_product.inserted_id}
            )
            created_products.append(created_product)
    return (
        created_products
        if len(new_products) != 1 or len(created_products) != 1
        else created_products[0]
    )


async def list_products(database):
    products = database.product_collection.find()
    products = await products.to_list(length=100)
    return products


async def list_product_by_id(database, product_id: str):
    if (
        product := await database.product_collection.find_one({"_id": product_id})
    ) is not None:
        return product
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product with ID {product_id} not found",
    )


async def update_product(database, product_id: str, product: ProductUpdate = Body(...)):
    product = {k: v for k, v in product.dict().items() if v is not None}

    if len(product) >= 1:
        update_result = await database.product_collection.update_one(
            {"_id": product_id}, {"$set": product}
        )

        if update_result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found",
            )

    if (
        existing_product := await database.product_collection.find_one(
            {"_id": product_id}
        )
    ) is not None:
        return existing_product

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product with ID {product_id} not found",
    )


async def delete_product(database, product_id: str):
    delete_result = await database.product_collection.delete_one({"_id": product_id})

    if delete_result.deleted_count == 1:
        return RedirectResponse("/products/", status_code=status.HTTP_303_SEE_OTHER)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product with ID {product_id} not found",
    )
