"""
Product routes module.

Handles CRUD operations for products.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .models import Product
from .schemas import ProductCreate, ProductUpdate, ProductOut
from ..db import get_session

router = APIRouter()


@router.get("/", response_model=List[ProductOut])
async def list_products(db: AsyncSession = Depends(get_session),skip: int = 0,limit: int = 100,):
    """
    List products with pagination.

    Args:
        db (AsyncSession): Database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.

    Returns:
        List[ProductOut]: List of products.
    """
    query = select(Product).offset(skip).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()
    return products


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int,db: AsyncSession = Depends(get_session),):
    """
    Get a specific product by ID.

    Args:
        product_id (int): Product ID.
        db (AsyncSession): Database session.

    Returns:
        ProductOut: The requested product.

    Raises:
        HTTPException: If product is not found.
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(product_in: ProductCreate,db: AsyncSession = Depends(get_session),):
    """
    Create a new product.

    Args:
        product_in (ProductCreate): Product data.
        db (AsyncSession): Database session.

    Returns:
        ProductOut: The created product.
    """
    product = Product(**product_in.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(product_id: int,product_in: ProductUpdate,db: AsyncSession = Depends(get_session),):
    """
    Update a product.

    Args:
        product_id (int): Product ID.
        product_in (ProductUpdate): Updated product data.
        db (AsyncSession): Database session.

    Returns:
        ProductOut: The updated product.

    Raises:
        HTTPException: If product is not found.
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    data = product_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(product, field, value)

    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int,db: AsyncSession = Depends(get_session)):
    """
    Delete a product.

    Args:
        product_id (int): Product ID.
        db (AsyncSession): Database session.

    Raises:
        HTTPException: If product is not found.
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    await db.delete(product)
    await db.commit()
    return None
