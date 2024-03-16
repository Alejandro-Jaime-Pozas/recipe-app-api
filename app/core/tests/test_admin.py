"""
Tests for the Django admin modifications.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Tests for Django admin."""

    # for some reason, this setUp builtin fn from TestCase class is in camelcase, but this is an exception
    def setUp(self):
        """Create user and client."""
        self.client = Client()  # for use in testing allows POST and GET requests
        # creating a test superuser
        self.admin_user = get_user_model().objects.create_superuser(
            'admin@example.com',
            'testpass123',
        )
        # force login of the admin user to be able to login as admin
        self.client.force_login(self.admin_user)
        # as admin user (forced login), create a test user without admin permissions
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
            name='Test User',
        )

    def test_users_list(self):
        """Test that users are listed on page."""
        url = reverse('admin:core_user_changelist')  # gets url for the user model; this syntax is found in django docs, uses 'core' app, 'user' model, 'changelist' as parameters split by '_'
        res = self.client.get(url)  # creates http GET request to url; this is only possible since there is forced_login

        # assert that the result contains the new non-admin user's name and email keys
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)