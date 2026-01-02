"""Product routes."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .models import Product, Category
from .schemas import ProductCreate, ProductUpdate, ProductOut, CategoryCreate, CategoryOut, CategoryUpdate
from ..db import get_session

router = APIRouter()


@router.get("/", response_model=List[ProductOut])
async def list_products(db: AsyncSession = Depends(get_session),skip: int = 0,limit: int = 100,):
    """List products."""
    query = select(Product).options(selectinload(Product.category)).offset(skip).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()
    return products


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int,db: AsyncSession = Depends(get_session),):
    """Get product by ID."""
    result = await db.execute(select(Product).options(selectinload(Product.category)).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(product_in: ProductCreate,db: AsyncSession = Depends(get_session),):
    """Create product."""

    product = Product(**product_in.model_dump())
    db.add(product)
    await db.commit()
    # Reload with relation for Pydantic response
    result = await db.execute(select(Product).options(selectinload(Product.category)).where(Product.id == product.id))
    product = result.scalar_one()
    return product


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(product_id: int,product_in: ProductUpdate,db: AsyncSession = Depends(get_session),):
    """Update product."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    data = product_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(product, field, value)


    db.add(product)
    await db.commit()
    # Reload with relation
    result = await db.execute(select(Product).options(selectinload(Product.category)).where(Product.id == product.id))
    product = result.scalar_one()
    return product



@router.post("/categories/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(category_in: CategoryCreate, db: AsyncSession = Depends(get_session)):
    """
    Create a new category.
    """
    category = Category(**category_in.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category



@router.get("/categories/", response_model=List[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_session), skip: int = 0, limit: int = 100):
    """
    List categories.
    """
    result = await db.execute(select(Category).offset(skip).limit(limit))
    categories = result.scalars().all()
    return categories


@router.put("/categories/{category_id}", response_model=CategoryOut)
async def update_category(category_id: int, category_in: CategoryUpdate, db: AsyncSession = Depends(get_session)):
    """
    Update a category.
    """
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    category.name = category_in.name
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int,db: AsyncSession = Depends(get_session)):
    """Delete product."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    await db.delete(product)
    await db.commit()
    return None
