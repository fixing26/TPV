"""
Tables routes module.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..db import get_session
from .models import Table
from .schemas import TableCreate, TableOut, TableUpdate

router = APIRouter()

@router.post("/", response_model=TableOut, status_code=status.HTTP_201_CREATED)
async def create_table(
    table_in: TableCreate,
    db: AsyncSession = Depends(get_session)
):
    # Check if exists
    result = await db.execute(select(Table).where(Table.name == table_in.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Table with this name already exists")

    new_table = Table(name=table_in.name, description=table_in.description)
    db.add(new_table)
    await db.commit()
    await db.refresh(new_table)
    return new_table

@router.get("/", response_model=List[TableOut])
async def list_tables(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
):
    result = await db.execute(select(Table).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{table_id}", response_model=TableOut)
async def get_table(
    table_id: int,
    db: AsyncSession = Depends(get_session)
):
    result = await db.execute(select(Table).where(Table.id == table_id))
    table = result.scalar_one_or_none()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table

@router.put("/{table_id}", response_model=TableOut)
async def update_table(
    table_id: int,
    table_in: TableCreate,
    db: AsyncSession = Depends(get_session)
):
    result = await db.execute(select(Table).where(Table.id == table_id))
    table = result.scalar_one_or_none()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    # Check name uniqueness if changed
    if table_in.name != table.name:
         exist_res = await db.execute(select(Table).where(Table.name == table_in.name))
         if exist_res.scalar_one_or_none():
             raise HTTPException(status_code=400, detail="Table with this name already exists")

    table.name = table_in.name
    table.description = table_in.description
    db.add(table)
    await db.commit()
    await db.refresh(table)
    return table

@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(
    table_id: int,
    db: AsyncSession = Depends(get_session)
):
    result = await db.execute(select(Table).where(Table.id == table_id))
    table = result.scalar_one_or_none()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    await db.delete(table)
    await db.commit()
    return None
