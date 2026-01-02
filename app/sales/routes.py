"""Sales routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload

from .models import Sale, SaleLine
from .schemas import SaleCreate, SaleOut, SaleOpen, SaleUpdate, SaleLineCreate
from ..products.models import Product
from ..auth.dependencies import get_current_user
from ..auth.models import User
from ..db import get_session
from ..tables.models import Table

router = APIRouter()


@router.post("/", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
async def create_sale(
    sale_in: SaleCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create new sale (Immediate Close)."""
    if not sale_in.lines:
        raise HTTPException(status_code=400, detail="La venta debe tener al menos una línea.")


    sale = Sale(
        total=0.0,
        payment_method=sale_in.payment_method,
        status="CLOSED",
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    db.add(sale)
    await db.flush()

    total = 0.0
    for line_in in sale_in.lines:
        result = await db.execute(select(Product).where(Product.id == line_in.product_id, Product.tenant_id == current_user.tenant_id))
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto {line_in.product_id} no encontrado")
        
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
        total += line_total
    
    sale.total = total
    db.add(sale)
    await db.commit()
    
    # Reload
    result = await db.execute(
        select(Sale)
        .options(
            selectinload(Sale.lines).joinedload(SaleLine.product).joinedload(Product.category),
            joinedload(Sale.creator),
            joinedload(Sale.closer)
        )
        .where(Sale.id == sale.id)
    )
    return result.unique().scalar_one()


@router.post("/open", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
async def open_account(
    account_in: SaleOpen,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Open new account/table."""
    # Check if table exists and is free if provided
    if account_in.table_id:
        # Check if table exists
        t_res = await db.execute(select(Table).where(Table.id == account_in.table_id, Table.tenant_id == current_user.tenant_id))
        table = t_res.scalar_one_or_none()
        if not table:
            raise HTTPException(status_code=404, detail="Mesa no encontrada")
        
        # Check if table already has an OPEN sale
        open_res = await db.execute(
            select(Sale)
            .where(Sale.table_id == account_in.table_id)
            .where(Sale.status == "OPEN")
        )
        if open_res.scalar_one_or_none():
             raise HTTPException(status_code=400, detail="La mesa ya tiene una cuenta abierta")

    sale = Sale(
        total=0.0,
        status="OPEN",
        table_id=account_in.table_id,
        name=account_in.name,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    db.add(sale)
    await db.commit()
    await db.refresh(sale)
    
    # Reload with full options
    result = await db.execute(
        select(Sale)
        .options(
            selectinload(Sale.lines).joinedload(SaleLine.product).joinedload(Product.category),
            joinedload(Sale.creator),
            joinedload(Sale.closer)
        )
        .where(Sale.id == sale.id)
    )
    return result.unique().scalar_one()


@router.get("/active", response_model=List[SaleOut])
async def list_active_accounts(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """List OPEN accounts."""
    result = await db.execute(
        select(Sale)
        .options(
            selectinload(Sale.lines).joinedload(SaleLine.product).joinedload(Product.category),
            joinedload(Sale.creator),
            joinedload(Sale.closer)
        )
        .where(Sale.status == "OPEN", Sale.tenant_id == current_user.tenant_id)
        .order_by(Sale.created_at.desc())
    )
    return result.unique().scalars().all()


@router.post("/{sale_id}/lines", response_model=SaleOut)
async def add_lines_to_account(
    sale_id: int,
    lines_in: List[SaleLineCreate],
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Add items to account."""
    result = await db.execute(select(Sale).where(Sale.id == sale_id, Sale.tenant_id == current_user.tenant_id))
    sale = result.scalar_one_or_none()
    
    if not sale:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    
    if sale.status != "OPEN":
        raise HTTPException(status_code=400, detail="La cuenta no está abierta")

    total_added = 0.0
    for line_in in lines_in:
        # Check product
        p_res = await db.execute(select(Product).where(Product.id == line_in.product_id, Product.tenant_id == current_user.tenant_id))
        product = p_res.scalar_one_or_none()
        if not product:
             raise HTTPException(status_code=404, detail=f"Producto {line_in.product_id} no encontrado")
        
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
        total_added += line_total
    
    sale.total += total_added
    db.add(sale)
    await db.commit()
    
    # Reload with full options
    result = await db.execute(
        select(Sale)
        .options(
            selectinload(Sale.lines).joinedload(SaleLine.product).joinedload(Product.category),
            joinedload(Sale.creator),
            joinedload(Sale.closer)
        )
        .where(Sale.id == sale.id)
    )
    return result.unique().scalar_one()


@router.put("/{sale_id}", response_model=SaleOut)
async def update_sale(
    sale_id: int,
    sale_in: SaleUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update sale (replace lines)."""
    # Load with collection to cleanly delete/update
    result = await db.execute(select(Sale).options(selectinload(Sale.lines)).where(Sale.id == sale_id, Sale.tenant_id == current_user.tenant_id))
    sale = result.scalar_one_or_none()
    
    if not sale:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    
    if sale.status != "OPEN":
        raise HTTPException(status_code=400, detail="La cuenta no está abierta")

    # Prepare new lines
    new_lines = []
    total = 0.0
    for line_in in sale_in.lines:
        p_res = await db.execute(select(Product).where(Product.id == line_in.product_id, Product.tenant_id == current_user.tenant_id))
        product = p_res.scalar_one_or_none()
        if not product:
             raise HTTPException(status_code=404, detail=f"Producto {line_in.product_id} no encontrado")
        
        price_unit = product.price
        line_total = price_unit * line_in.quantity
        
        sale_line = SaleLine(
            product_id=product.id,
            quantity=line_in.quantity,
            price_unit=price_unit,
            line_total=line_total,
        )
        new_lines.append(sale_line)
        total += line_total
    
    # Replace lines (cascade deletes old ones)
    sale.lines = new_lines
    sale.total = total
    
    db.add(sale)
    await db.commit()
    
    # Reload with full options
    result = await db.execute(
        select(Sale)
        .options(
            selectinload(Sale.lines).joinedload(SaleLine.product).joinedload(Product.category),
            joinedload(Sale.creator),
            joinedload(Sale.closer)
        )
        .where(Sale.id == sale.id)
    )
    return result.unique().scalar_one()


@router.post("/{sale_id}/close", response_model=SaleOut)
async def close_account(
    sale_id: int,
    payment_method: str = "cash",
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Close (checkout) account."""
    result = await db.execute(
        select(Sale)
        .where(Sale.id == sale_id, Sale.tenant_id == current_user.tenant_id)
    )
    sale = result.scalar_one_or_none()
    
    if not sale:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    
    if sale.status != "OPEN":
        raise HTTPException(status_code=400, detail="La cuenta ya está cerrada o cancelada")
    
    sale.status = "CLOSED"
    sale.payment_method = payment_method
    sale.closed_by_id = current_user.id
    db.add(sale)
    await db.commit()
    
    # Reload relationship to return updated data
    result = await db.execute(
        select(Sale)
        .options(
            selectinload(Sale.lines).joinedload(SaleLine.product).joinedload(Product.category),
            joinedload(Sale.creator),
            joinedload(Sale.closer)
        )
        .where(Sale.id == sale.id)
    )
    return result.unique().scalar_one()


@router.get("/", response_model=List[SaleOut])
async def list_sales(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """List sales."""
    result = await db.execute(
        select(Sale)
        .options(
            selectinload(Sale.lines).joinedload(SaleLine.product).joinedload(Product.category),
            joinedload(Sale.creator),
            joinedload(Sale.closer)
        )
        .where(Sale.tenant_id == current_user.tenant_id)
        .offset(skip)
        .limit(limit)
        .order_by(Sale.created_at.desc())
    )
    return result.unique().scalars().all()


@router.get("/{sale_id}", response_model=SaleOut)
async def get_sale(
    sale_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get sale by ID."""
    result = await db.execute(
        select(Sale)
        .options(
            selectinload(Sale.lines).joinedload(SaleLine.product).joinedload(Product.category),
            joinedload(Sale.creator),
            joinedload(Sale.closer)
        )
        .where(Sale.id == sale_id, Sale.tenant_id == current_user.tenant_id)
    )
    sale = result.unique().scalar_one_or_none()
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")

    return sale
