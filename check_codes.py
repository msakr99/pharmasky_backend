#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from market.models import ProductCode, StoreProductCode
from accounts.models import User

# Check ProductCode data
print("=== ProductCode Data ===")
product_codes = ProductCode.objects.all()
print(f"Total ProductCode count: {product_codes.count()}")

if product_codes.exists():
    print("Sample ProductCode entries:")
    for pc in product_codes[:10]:
        print(f"  Code: {pc.code}, User: {pc.user.id if pc.user else 'None'}, Product: {pc.product.name if pc.product else 'None'}")

# Check StoreProductCode data
print("\n=== StoreProductCode Data ===")
store_product_codes = StoreProductCode.objects.all()
print(f"Total StoreProductCode count: {store_product_codes.count()}")

if store_product_codes.exists():
    print("Sample StoreProductCode entries:")
    for spc in store_product_codes[:10]:
        print(f"  Code: {spc.code}, Store: {spc.store.id if spc.store else 'None'}, Product: {spc.product.name if spc.product else 'None'}")

# Check specific codes that are failing
print("\n=== Checking Specific Codes ===")
test_codes = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42]

for code in test_codes:
    pc_exists = ProductCode.objects.filter(code=code).exists()
    spc_exists = StoreProductCode.objects.filter(code=code).exists()
    print(f"Code {code}: ProductCode={pc_exists}, StoreProductCode={spc_exists}")

# Check users
print("\n=== Users ===")
users = User.objects.all()
print(f"Total users: {users.count()}")
for user in users[:5]:
    print(f"  User ID: {user.id}, Role: {user.role}")
