

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .models import Product, Category
from .schemas import ProductCreate, ProductUpdate, ProductOut, CategoryCreate, CategoryOut, CategoryUpdate
from ..db import get_session
from ..auth.dependencies import get_current_user
from ..auth.models import User

router = APIRouter()


@router.get("/", response_model=List[ProductOut])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    query = select(Product).options(selectinload(Product.category)).where(Product.tenant_id == current_user.tenant_id).offset(skip).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()
    return products


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    result = await db.execute(select(Product).options(selectinload(Product.category)).where(Product.id == product_id, Product.tenant_id == current_user.tenant_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    
    # Verify Category belongs to tenant
    cat_res = await db.execute(select(Category).where(Category.id == product_in.category_id, Category.tenant_id == current_user.tenant_id))
    if not cat_res.scalar_one_or_none():
         raise HTTPException(status_code=400, detail="Categoría no válida")

    product = Product(**product_in.model_dump())
    product.tenant_id = current_user.tenant_id # Assign Tenant
    db.add(product)
    await db.commit()
    # Reload with relation for Pydantic response
    result = await db.execute(select(Product).options(selectinload(Product.category)).where(Product.id == product.id))
    product = result.scalar_one()
    return product


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    result = await db.execute(select(Product).where(Product.id == product_id, Product.tenant_id == current_user.tenant_id))
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
async def create_category(
    category_in: CategoryCreate, 
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    category = Category(**category_in.model_dump())
    category.tenant_id = current_user.tenant_id
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.get("/categories/", response_model=List[CategoryOut])
async def list_categories(
    skip: int = 0, 
    limit: int = 100,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    result = await db.execute(select(Category).where(Category.tenant_id == current_user.tenant_id).offset(skip).limit(limit))
    categories = result.scalars().all()
    return categories


@router.put("/categories/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: int, 
    category_in: CategoryUpdate, 
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    result = await db.execute(select(Category).where(Category.id == category_id, Category.tenant_id == current_user.tenant_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    category.name = category_in.name
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    result = await db.execute(select(Product).where(Product.id == product_id, Product.tenant_id == current_user.tenant_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    await db.delete(product)
    await db.commit()
    return None
