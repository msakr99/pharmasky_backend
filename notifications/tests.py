"""
Tests for the notifications app.

This module provides comprehensive tests for notifications functionality.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

from notifications.models import Notification, Topic, TopicSubscription


User = get_user_model()


class NotificationModelTest(TestCase):
    """Test cases for Notification model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            role="PHARMACY"
        )
        self.topic = Topic.objects.create(
            name="Test Topic",
            description="Test topic description"
        )
    
    def test_notification_creation(self):
        """Test creating a notification."""
        notification = Notification.objects.create(
            user=self.user,
            title="Test Notification",
            message="This is a test notification",
            is_read=False
        )
        
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.title, "Test Notification")
        self.assertFalse(notification.is_read)
        self.assertIsNotNone(notification.created_at)
    
    def test_notification_with_topic(self):
        """Test creating a notification with a topic."""
        notification = Notification.objects.create(
            user=self.user,
            topic=self.topic,
            title="Topic Notification",
            message="This is a topic notification"
        )
        
        self.assertEqual(notification.topic, self.topic)
        self.assertIn(notification, self.topic.notifications.all())
    
    def test_notification_ordering(self):
        """Test that notifications are ordered by created_at descending."""
        notif1 = Notification.objects.create(
            user=self.user,
            title="First",
            message="First notification"
        )
        notif2 = Notification.objects.create(
            user=self.user,
            title="Second",
            message="Second notification"
        )
        
        notifications = Notification.objects.all()
        self.assertEqual(notifications[0], notif2)
        self.assertEqual(notifications[1], notif1)


class TopicModelTest(TestCase):
    """Test cases for Topic model."""
    
    def test_topic_creation(self):
        """Test creating a topic."""
        topic = Topic.objects.create(
            name="News",
            description="News and updates"
        )
        
        self.assertEqual(topic.name, "News")
        self.assertEqual(str(topic), "News")
    
    def test_topic_unique_name(self):
        """Test that topic names are unique."""
        Topic.objects.create(name="Unique Topic")
        
        with self.assertRaises(Exception):
            Topic.objects.create(name="Unique Topic")


class TopicSubscriptionModelTest(TestCase):
    """Test cases for TopicSubscription model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            role="PHARMACY"
        )
        self.topic = Topic.objects.create(name="Test Topic")
    
    def test_subscription_creation(self):
        """Test creating a topic subscription."""
        subscription = TopicSubscription.objects.create(
            user=self.user,
            topic=self.topic,
            is_active=True
        )
        
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.topic, self.topic)
        self.assertTrue(subscription.is_active)
    
    def test_subscription_unique_together(self):
        """Test that user-topic combination is unique."""
        TopicSubscription.objects.create(
            user=self.user,
            topic=self.topic
        )
        
        with self.assertRaises(Exception):
            TopicSubscription.objects.create(
                user=self.user,
                topic=self.topic
            )


class NotificationAPITest(APITestCase):
    """Test cases for Notification API endpoints."""
    
    def setUp(self):
        """Set up test data and authentication."""
        self.client = APIClient()
        
        # Create users
        self.pharmacy_user = User.objects.create_user(
            username="pharmacy",
            password="testpass123",
            role="PHARMACY"
        )
        self.admin_user = User.objects.create_user(
            username="admin",
            password="testpass123",
            role="ADMIN"
        )
        
        # Create topic
        self.topic = Topic.objects.create(
            name="Test Topic",
            description="Test description"
        )
        
        # Create notifications
        self.notification1 = Notification.objects.create(
            user=self.pharmacy_user,
            title="Test Notification 1",
            message="Test message 1",
            is_read=False
        )
        self.notification2 = Notification.objects.create(
            user=self.pharmacy_user,
            title="Test Notification 2",
            message="Test message 2",
            is_read=True
        )
    
    def test_list_notifications_authenticated(self):
        """Test listing notifications for authenticated user."""
        self.client.force_authenticate(user=self.pharmacy_user)
        
        url = reverse("notifications:notifications-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
    
    def test_list_notifications_unauthenticated(self):
        """Test that unauthenticated users cannot list notifications."""
        url = reverse("notifications:notifications-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_unread_notifications(self):
        """Test listing only unread notifications."""
        self.client.force_authenticate(user=self.pharmacy_user)
        
        url = reverse("notifications:notifications-unread-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertFalse(response.data["results"][0]["is_read"])
    
    def test_retrieve_notification(self):
        """Test retrieving a single notification."""
        self.client.force_authenticate(user=self.pharmacy_user)
        
        url = reverse("notifications:notifications-detail", kwargs={"pk": self.notification1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.notification1.pk)
    
    def test_update_notification_mark_as_read(self):
        """Test updating notification to mark as read."""
        self.client.force_authenticate(user=self.pharmacy_user)
        
        url = reverse("notifications:notifications-update", kwargs={"pk": self.notification1.pk})
        data = {"is_read": True}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify notification is marked as read
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)
    
    def test_mark_all_notifications_as_read(self):
        """Test marking all notifications as read."""
        self.client.force_authenticate(user=self.pharmacy_user)
        
        url = reverse("notifications:notifications-mark-all-read")
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify all notifications are marked as read
        unread_count = Notification.objects.filter(
            user=self.pharmacy_user,
            is_read=False
        ).count()
        self.assertEqual(unread_count, 0)
    
    def test_delete_notification(self):
        """Test deleting a notification."""
        self.client.force_authenticate(user=self.pharmacy_user)
        
        url = reverse("notifications:notifications-delete", kwargs={"pk": self.notification1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify notification is deleted
        self.assertFalse(Notification.objects.filter(pk=self.notification1.pk).exists())
    
    def test_create_notification_admin_only(self):
        """Test that only admin can create notifications."""
        # Try with pharmacy user (should fail)
        self.client.force_authenticate(user=self.pharmacy_user)
        
        url = reverse("notifications:notifications-create")
        data = {
            "user": self.pharmacy_user.pk,
            "title": "New Notification",
            "message": "New message"
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try with admin user (should succeed)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_notification_stats(self):
        """Test getting notification statistics."""
        self.client.force_authenticate(user=self.pharmacy_user)
        
        url = reverse("notifications:notifications-stats")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["total"], 2)
        self.assertEqual(response.data["data"]["unread"], 1)
        self.assertEqual(response.data["data"]["read"], 1)


class TopicAPITest(APITestCase):
    """Test cases for Topic API endpoints."""
    
    def setUp(self):
        """Set up test data and authentication."""
        self.client = APIClient()
        
        # Create users
        self.pharmacy_user = User.objects.create_user(
            username="pharmacy",
            password="testpass123",
            role="PHARMACY"
        )
        self.admin_user = User.objects.create_user(
            username="admin",
            password="testpass123",
            role="ADMIN"
        )
        
        # Create topic
        self.topic = Topic.objects.create(
            name="Test Topic",
            description="Test description"
        )
    
    def test_list_topics(self):
        """Test listing all topics."""
        self.client.force_authenticate(user=self.pharmacy_user)
        
        url = reverse("notifications:topics-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)
    
    def test_retrieve_topic(self):
        """Test retrieving a single topic."""
        self.client.force_authenticate(user=self.pharmacy_user)
        
        url = reverse("notifications:topics-detail", kwargs={"pk": self.topic.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.topic.pk)
    
    def test_create_topic_admin_only(self):
        """Test that only admin can create topics."""
        # Try with pharmacy user (should fail)
        self.client.force_authenticate(user=self.pharmacy_user)
        
        url = reverse("notifications:topics-create")
        data = {
            "name": "New Topic",
            "description": "New description"
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try with admin user (should succeed)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TopicSubscriptionAPITest(APITestCase):
    """Test cases for TopicSubscription API endpoints."""
    
    def setUp(self):
        """Set up test data and authentication."""
        self.client = APIClient()
        
        # Create user
        self.pharmacy_user = User.objects.create_user(
            username="pharmacy",
            password="testpass123",
            role="PHARMACY"
        )
        
        # Create topics
        self.topic1 = Topic.objects.create(name="Topic 1")
        self.topic2 = Topic.objects.create(name="Topic 2")
        
        # Create subscription
        self.subscription = TopicSubscription.objects.create(
            user=self.pharmacy_user,
            topic=self.topic1,
            is_active=True
        )
    
    def test_list_subscriptions(self):
        """Test listing user's subscriptions."""
        self.client.force_authenticate(user=self.pharmacy_user)
        
        url = reverse("notifications:subscriptions-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
    
    def test_create_subscription(self):
        """Test subscribing to a topic."""
        self.client.force_authenticate(user=self.pharmacy_user)
        
        url = reverse("notifications:subscriptions-create")
        data = {
            "topic": self.topic2.pk,
            "is_active": True
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify subscription created
        self.assertTrue(
            TopicSubscription.objects.filter(
                user=self.pharmacy_user,
                topic=self.topic2
            ).exists()
        )
    
    def test_update_subscription(self):
        """Test updating subscription status."""
        self.client.force_authenticate(user=self.pharmacy_user)
        
        url = reverse("notifications:subscriptions-update", kwargs={"pk": self.subscription.pk})
        data = {"is_active": False}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify subscription deactivated
        self.subscription.refresh_from_db()
        self.assertFalse(self.subscription.is_active)
    
    def test_delete_subscription(self):
        """Test unsubscribing from a topic."""
        self.client.force_authenticate(user=self.pharmacy_user)
        
        url = reverse("notifications:subscriptions-delete", kwargs={"pk": self.subscription.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify subscription deleted
        self.assertFalse(
            TopicSubscription.objects.filter(pk=self.subscription.pk).exists()
        )
    
    def test_my_topics(self):
        """Test getting all topics with subscription status."""
        self.client.force_authenticate(user=self.pharmacy_user)
        
        url = reverse("notifications:my-topics")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["data"]), 0)
        
        # Check that subscription status is included
        for topic_data in response.data["data"]:
            self.assertIn("is_subscribed", topic_data)
            self.assertIn("subscription_active", topic_data)
