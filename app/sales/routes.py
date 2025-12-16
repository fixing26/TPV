"""
Sales routes module.

Handles creation and retrieval of sales (tickets).
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .models import Sale, SaleLine
from .schemas import SaleCreate, SaleOut
from ..products.models import Product
from ..auth.dependencies import get_current_user
from ..auth.models import User
from ..db import get_session

router = APIRouter()


@router.post("/", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
async def create_sale(
    sale_in: SaleCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new sale (ticket).

    Calculates the total based on product prices and updates stock.

    Args:
        sale_in (SaleCreate): Sale data including lines.
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.

    Returns:
        SaleOut: The created sale with full details.

    Raises:
        HTTPException: If a product is not found or stock is insufficient.
    """
    if not sale_in.lines:
        raise HTTPException(status_code=400, detail="La venta debe tener al menos una línea.")

    # Creamos la venta con total 0 y luego calculamos
    sale = Sale(
        total=0.0,
        payment_method=sale_in.payment_method,
        user_id=current_user.id
    )
    db.add(sale)
    await db.flush()  # para tener sale.id antes del commit

    total = 0.0

    for line_in in sale_in.lines:
        # Buscar producto
        result = await db.execute(
            select(Product).where(Product.id == line_in.product_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Producto {line_in.product_id} no encontrado",
            )

        price_unit = product.price
        line_total = price_unit * line_in.quantity

        sale_line = SaleLine(
            sale_id=sale.id,
            product_id=product.id,
            quantity=line_in.quantity,
            price_unit=price_unit,
            line_total=line_total,
        )
        db.add(sale_line)

        # Actualizar total de la venta
        total += line_total

    sale.total = total
    db.add(sale)

    await db.commit()

    # Volvemos a consultar la venta con sus líneas para devolverla completa
    result = await db.execute(
        select(Sale)
        .options(selectinload(Sale.lines))
        .where(Sale.id == sale.id)
    )
    sale_db = result.scalar_one()

    return sale_db


@router.get("/", response_model=List[SaleOut])
async def list_sales(db: AsyncSession = Depends(get_session),skip: int = 0,limit: int = 100,):
    """
    List sales with pagination.

    Args:
        db (AsyncSession): Database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.

    Returns:
        List[SaleOut]: List of sales.
    """
    result = await db.execute(
        select(Sale)
        .options(selectinload(Sale.lines))
        .offset(skip)
        .limit(limit)
        .order_by(Sale.created_at.desc())
    )
    sales = result.scalars().all()
    return sales


@router.get("/{sale_id}", response_model=SaleOut)
async def get_sale(sale_id: int,db: AsyncSession = Depends(get_session),):
    """
    Get a specific sale by ID.

    Args:
        sale_id (int): Sale ID.
        db (AsyncSession): Database session.

    Returns:
        SaleOut: The requested sale.

    Raises:
        HTTPException: If sale is not found.
    """
    result = await db.execute(
        select(Sale)
        .options(selectinload(Sale.lines))
        .where(Sale.id == sale_id)
    )
    sale = result.scalar_one_or_none()
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")

    return sale

