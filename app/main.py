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
from app.products.models import Product, Category
from app.sales.models import Sale, SaleLine
from app.cash_closing.models import CashClosing
from app.tables.models import Table


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
from app.tables.routes import router as tables_router

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(products_router, prefix="/products", tags=["Products"])
app.include_router(sales_router, prefix="/sales", tags=["Sales"])
app.include_router(cash_closing_router, prefix="/cash-closing", tags=["Cash Closing"])
app.include_router(tables_router, prefix="/tables", tags=["Tables"])

# Servir archivos estáticos (Frontend)
# Aseguramos que el directorio exista, aunque sea vacío por ahora
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# --- CACHE BUSTING / VERSIÓN AUTOMÁTICA ---
from app.core.static_handler import get_static_handler
serve_static_html = get_static_handler(static_dir)

@app.get("/", include_in_schema=False)
async def serve_root():
    return await serve_static_html("index.html")

@app.get("/{filename}.html", include_in_schema=False)
async def serve_html_page(filename: str):
    """
    Intercepta peticiones a archivos .html para inyectar versiones (?v=timestamp)
    en los enlaces a CSS y JS locales.
    """
    return await serve_static_html(f"{filename}.html")

# Montar StaticFiles para el resto de recursos (CSS, JS, imágenes, etc.)
# Nota: StaticFiles servirá los archivos ignorando los query params (?v=...)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
