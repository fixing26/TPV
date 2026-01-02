import pytest
import asyncio
from httpx import AsyncClient
import sys
import os
sys.path.append(os.getcwd())

from app.main import app
from app.db import async_session
from app.auth.models import User
from app.products.models import Product, Category
from sqlalchemy import select, delete

@pytest.mark.asyncio
async def test_tenant_isolation():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        
        # 1. Register Admin A (Tenant A)
        user_a_data = {"username": "admin_a", "password": "password", "role": "admin"}
        resp_a = await ac.post("/auth/register", json=user_a_data)
        if resp_a.status_code == 400: # Cleanup if exists
             # This is a manual script, we might restart DB or clean manually. 
             # For now assume clean state or new random users
             import uuid
             user_a_data["username"] = f"admin_a_{uuid.uuid4().hex[:4]}"
             resp_a = await ac.post("/auth/register", json=user_a_data)

        assert resp_a.status_code == 200
        token_a = (await ac.post("/auth/login", json=user_a_data)).json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # 2. Register Admin B (Tenant B)
        user_b_data = {"username": "admin_b", "password": "password", "role": "admin"}
        resp_b = await ac.post("/auth/register", json=user_b_data)
        if resp_b.status_code == 400:
             import uuid
             user_b_data["username"] = f"admin_b_{uuid.uuid4().hex[:4]}"
             resp_b = await ac.post("/auth/register", json=user_b_data)
             
        assert resp_b.status_code == 200
        token_b = (await ac.post("/auth/login", json=user_b_data)).json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # 3. Admin A creates Category
        cat_data = {"name": "Drinks A"}
        resp_cat_a = await ac.post("/products/categories/", json=cat_data, headers=headers_a)
        assert resp_cat_a.status_code == 201
        cat_id_a = resp_cat_a.json()["id"]

        # 4. Admin B tries to list categories -> Should NOT see Drinks A
        resp_list_b = await ac.get("/products/categories/", headers=headers_b)
        assert resp_list_b.status_code == 200
        cats_b = resp_list_b.json()
        assert not any(c["id"] == cat_id_a for c in cats_b)

        # 5. Admin B creates Category with SAME NAME "Drinks A" -> Should succeed (different tenant)
        resp_cat_b = await ac.post("/products/categories/", json=cat_data, headers=headers_b)
        assert resp_cat_b.status_code == 201
        
        # 6. Admin A creates internal user "employee_a"
        emp_a_data = {"username": f"emp_a_{user_a_data['username']}", "password": "password", "role": "cashier"}
        resp_emp = await ac.post("/auth/create_user", json=emp_a_data, headers=headers_a)
        assert resp_emp.status_code == 200
        
        # 7. Log in as employee_a and check if they see Admin A's category
        token_emp = (await ac.post("/auth/login", json=emp_a_data)).json()["access_token"]
        headers_emp = {"Authorization": f"Bearer {token_emp}"}
        
        resp_list_emp = await ac.get("/products/categories/", headers=headers_emp)
        assert resp_list_emp.status_code == 200
        cats_emp = resp_list_emp.json()
        assert any(c["id"] == cat_id_a for c in cats_emp) # Should see Admin A's category

        print("Verification Passed: Multi-tenancy isolation confirmed.")

if __name__ == "__main__":
    asyncio.run(test_tenant_isolation())
