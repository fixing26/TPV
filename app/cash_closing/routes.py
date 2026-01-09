
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from ..db import get_session
from .models import CashClosing
from .schemas import CashClosingOut
from ..sales.models import Sale
from ..auth.dependencies import get_current_user
from ..auth.models import User

router = APIRouter()

@router.post("/", response_model=CashClosingOut)
async def create_cash_closing(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    stmt_ranges = select(
        func.min(Sale.id),
        func.max(Sale.id),
        func.min(Sale.created_at),
        func.max(Sale.created_at),
        func.count(Sale.id),
        func.sum(Sale.total)
    ).where(Sale.tenant_id == current_user.tenant_id)

    result_ranges = await db.execute(stmt_ranges)
    min_id, max_id, min_date, max_date, count, grand_total = result_ranges.one()
    
    if not count or count == 0:
        raise HTTPException(status_code=400, detail="No hay ventas para cerrar")

    # Get totals by payment method
    # Cash
    stmt_cash = select(func.sum(Sale.total)).where(Sale.payment_method == "cash", Sale.tenant_id == current_user.tenant_id)
    result_cash = await db.execute(stmt_cash)
    total_cash = result_cash.scalar() or 0.0

    # Card
    stmt_card = select(func.sum(Sale.total)).where(Sale.payment_method == "card", Sale.tenant_id == current_user.tenant_id)
    result_card = await db.execute(stmt_card)
    total_card = result_card.scalar() or 0.0

    # Create Closing Record
    closing = CashClosing(
        closing_type="X",
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        from_sales=min_id,
        to_sales=max_id,
        from_date=min_date,
        to_date=max_date,
        total_sales=count,
        total_cash=total_cash,
        total_card=total_card,
        total_total=grand_total or 0.0
    )
    
    db.add(closing)
    await db.flush() # Get ID
    await db.refresh(closing)
    
    await db.commit()
    
    return closing

@router.delete("/sales", response_model=CashClosingOut)
async def delete_sales(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    stmt_ranges = select(
        func.min(Sale.id),
        func.max(Sale.id),
        func.min(Sale.created_at),
        func.max(Sale.created_at),
        func.count(Sale.id),
        func.sum(Sale.total)
    ).where(Sale.tenant_id == current_user.tenant_id)
    
    result_ranges = await db.execute(stmt_ranges)
    min_id, max_id, min_date, max_date, count, grand_total = result_ranges.one()
    
    if not count or count == 0:
        raise HTTPException(status_code=400, detail="No hay ventas para cerrar")

    # Get totals by payment method
    # Cash
    stmt_cash = select(func.sum(Sale.total)).where(Sale.payment_method == "cash", Sale.tenant_id == current_user.tenant_id)
    result_cash = await db.execute(stmt_cash)
    total_cash = result_cash.scalar() or 0.0

    # Card
    stmt_card = select(func.sum(Sale.total)).where(Sale.payment_method == "card", Sale.tenant_id == current_user.tenant_id)
    result_card = await db.execute(stmt_card)
    total_card = result_card.scalar() or 0.0

    # Create Closing Record
    closing = CashClosing(
        closing_type="Z",
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        from_sales=min_id,
        to_sales=max_id,
        from_date=min_date,
        to_date=max_date,
        total_sales=count,
        total_cash=total_cash,
        total_card=total_card,
        total_total=grand_total or 0.0
    )
    
    db.add(closing)
    await db.flush() # Get ID
    await db.refresh(closing)
    await db.commit()

    result_sales_to_delete = await db.execute(
        select(Sale).where(Sale.id.between(min_id, max_id), Sale.tenant_id == current_user.tenant_id)
    )
    sales_to_delete = result_sales_to_delete.scalars().all()
    try:
        for sale in sales_to_delete:
            await db.delete(sale)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    await db.commit()
    return closing