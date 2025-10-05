#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from accounts.models import User
from accounts.choices import Role

# Update test user role
print("=== Updating User Role ===")
try:
    user = User.objects.get(username='testuser')
    print(f"Current User: {user.username}, Role: {user.role}, Is Staff: {user.is_staff}")
    
    # Change role to SALES
    user.role = Role.SALES
    user.save()
    
    print("Updated user role to SALES")
    
    # Check updated user
    user.refresh_from_db()
    print(f"Updated User: {user.username}, Role: {user.role}, Is Staff: {user.is_staff}")
    
except Exception as e:
    print(f"Error updating user: {e}")
