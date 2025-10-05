#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from accounts.models import User

# Check users
print("=== Users in Database ===")
users = User.objects.all()
print(f"Total users: {users.count()}")

for user in users:
    print(f"ID: {user.id}, Username: {user.username}, Role: {user.role}, Name: {user.name}")

# Check if we can create a test user
print("\n=== Creating Test User ===")
try:
    test_user = User.objects.create_user(
        username='testuser',
        password='testpass123',
        name='Test User',
        role='STORE'
    )
    print(f"Created test user: {test_user.username}")
except Exception as e:
    print(f"Error creating user: {e}")
