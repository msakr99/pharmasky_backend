#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from accounts.models import User

# Update test user permissions
print("=== Updating User Permissions ===")
try:
    user = User.objects.get(username='testuser')
    print(f"User: {user.username}, Role: {user.role}, Is Staff: {user.is_staff}, Is Superuser: {user.is_superuser}")
    
    # Give staff permissions
    user.is_staff = True
    user.save()
    
    print("Updated user permissions - is_staff = True")
    
    # Check updated user
    user.refresh_from_db()
    print(f"Updated User: {user.username}, Role: {user.role}, Is Staff: {user.is_staff}, Is Superuser: {user.is_superuser}")
    
except Exception as e:
    print(f"Error updating user: {e}")
