"""
Main application entry point.

This module configures the FastAPI application, including:
- Database connection management (lifespan).
- CORS middleware configuration.
- Router inclusion (Auth, Products, Sales).
- Static file serving for the frontend.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.db import engine, Base

# Importa todos los modelos para registrarlos
from app.auth.models import User
from app.products.models import Product
from app.sales.models import Sale, SaleLine
from app.cash_closing.models import CashClosing


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.

    Handles startup and shutdown events.
    - Startup: Creates database tables if they don't exist.
    - Shutdown: Performs cleanup (currently empty).
    """
    # --- STARTUP ---
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Tablas creadas/verificadas en Neon")
    yield  # ← Aquí se entrega el control a la app

    # --- SHUTDOWN ---
    # (normalmente no hacemos nada aquí, pero lo dejo para expandir)
    print("Cerrando aplicación…")


app = FastAPI(title="TPV API", lifespan=lifespan)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringir esto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
from app.auth.routes import router as auth_router
from app.products.routes import router as products_router
from app.sales.routes import router as sales_router
from app.cash_closing.routes import router as cash_closing_router

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(products_router, prefix="/products", tags=["Products"])
app.include_router(sales_router, prefix="/sales", tags=["Sales"])
app.include_router(cash_closing_router, prefix="/cash-closing", tags=["Cash Closing"])

# Servir archivos estáticos (Frontend)
# Aseguramos que el directorio exista, aunque sea vacío por ahora
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
