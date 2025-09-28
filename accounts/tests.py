"""
Tests for accounts application.

This module contains unit and integration tests for the accounts app,
including user models, authentication, and permissions.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Area, Pharmacy, Delivery, Sales
from accounts.choices import Role

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model."""
    
    def setUp(self):
        """Set up test data."""
        self.area = Area.objects.create(name="Test Area")
        
    def test_user_creation(self):
        """Test basic user creation."""
        user = User.objects.create_user(
            username="+201234567890",
            name="Test User",
            role=Role.PHARMACY,
            area=self.area
        )
        self.assertEqual(user.username.as_e164, "+201234567890")
        self.assertEqual(user.name, "Test User")
        self.assertEqual(user.role, Role.PHARMACY)
        self.assertEqual(user.area, self.area)
        
    def test_pharmacy_proxy_model(self):
        """Test Pharmacy proxy model functionality."""
        pharmacy = Pharmacy.objects.create_user(
            username="+201234567891",
            name="Test Pharmacy",
            area=self.area
        )
        self.assertEqual(pharmacy.role, Role.PHARMACY)
        
    def test_user_str_method(self):
        """Test User string representation."""
        user = User(name="Test User")
        self.assertEqual(str(user), "Test User")


class AreaModelTest(TestCase):
    """Test cases for Area model."""
    
    def test_area_creation(self):
        """Test area creation and string representation."""
        area = Area.objects.create(name="Cairo")
        self.assertEqual(area.name, "Cairo")
        self.assertEqual(str(area), "Cairo")


# TODO: Add more comprehensive tests for:
# - User permissions and roles
# - User managers and querysets
# - Authentication flows
# - Model validators
