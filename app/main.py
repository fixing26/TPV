

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.db import engine, Base

# Register models
from app.auth.models import User
from app.products.models import Product, Category
from app.sales.models import Sale, SaleLine
from app.cash_closing.models import CashClosing
from app.tables.models import Table


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Migration hack: Add closed_by_id if not exists
        from sqlalchemy import text
        try:
             await conn.execute(text("ALTER TABLE sales ADD COLUMN IF NOT EXISTS closed_by_id INTEGER REFERENCES users(id);"))
             
             # Multi-tenancy Migrations
             # Define a default tenant for existing legacy data
             default_tenant = "legacy_tenant"

             # Users
             await conn.execute(text(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS tenant_id VARCHAR DEFAULT '{default_tenant}';"))
             await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_tenant_id ON users (tenant_id);"))
             
             # Products
             await conn.execute(text(f"ALTER TABLE products ADD COLUMN IF NOT EXISTS tenant_id VARCHAR DEFAULT '{default_tenant}';"))
             await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_products_tenant_id ON products (tenant_id);"))
             # Extra fixes for products
             await conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS sku VARCHAR;"))
             await conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS category_id INTEGER REFERENCES categories(id);"))

             # Relax constraints for legacy unique constraints that might fail with multiple tenants
             # (Note: SQLite doesn't support dropping constraints easily in one line, but PostgreSQL does.
             # Assuming PostgreSQL based on error logs showing dialects/postgresql)
             
             # Categories
             await conn.execute(text(f"ALTER TABLE categories ADD COLUMN IF NOT EXISTS tenant_id VARCHAR DEFAULT '{default_tenant}';"))
             await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_categories_tenant_id ON categories (tenant_id);"))
             
             # Tables
             await conn.execute(text(f"ALTER TABLE tables ADD COLUMN IF NOT EXISTS tenant_id VARCHAR DEFAULT '{default_tenant}';"))
             await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tables_tenant_id ON tables (tenant_id);"))

             # Sales
             await conn.execute(text(f"ALTER TABLE sales ADD COLUMN IF NOT EXISTS tenant_id VARCHAR DEFAULT '{default_tenant}';"))
             await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_sales_tenant_id ON sales (tenant_id);"))

             # Cash Closings
             await conn.execute(text(f"ALTER TABLE cash_closings ADD COLUMN IF NOT EXISTS tenant_id VARCHAR DEFAULT '{default_tenant}';"))
             await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_cash_closings_tenant_id ON cash_closings (tenant_id);"))

             print("Migration: tenant_id columns checked/added.")
        except Exception as e:
             print(f"Migration error: {e}")


    print("Tablas verificadas")
    yield

    # Shutdown


app = FastAPI(title="TPV API", lifespan=lifespan)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# Static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Versioning
from app.core.static_handler import get_static_handler
serve_static_html = get_static_handler(static_dir)

@app.get("/", include_in_schema=False)
async def serve_root():
    return await serve_static_html("index.html")

@app.get("/{filename}.html", include_in_schema=False)
async def serve_html_page(filename: str):
    """Injects version params into HTML."""
    return await serve_static_html(f"{filename}.html")

# Mount static files
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
