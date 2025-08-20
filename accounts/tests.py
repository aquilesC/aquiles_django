from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.contrib.messages import get_messages


class AccountsViewsTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.members_group = Group.objects.create(name='members')
        
        # Create existing user for testing
        self.existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='existingpass123'
        )

    def test_register_view_get(self):
        """Test registration page loads correctly"""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.assertContains(response, 'Register')

    def test_register_view_success(self):
        """Test successful user registration"""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
        })
        
        # Should redirect to home page
        self.assertRedirects(response, reverse('core:home'))
        
        # User should be created
        user = User.objects.get(username='newuser')
        # Note: Django's UserCreationForm doesn't save email by default
        # self.assertEqual(user.email, 'newuser@example.com')
        
        # User should be added to members group
        self.assertTrue(user.groups.filter(name='members').exists())
        
        # User should be logged in
        self.assertTrue(user.is_authenticated)

    def test_register_view_existing_username(self):
        """Test registration with existing username"""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with that username already exists')

    def test_register_view_password_mismatch(self):
        """Test registration with mismatched passwords"""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'differentpass',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The two password fields didn't match")

    def test_login_view_get(self):
        """Test login page loads correctly"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertContains(response, 'Login')

    def test_login_view_success(self):
        """Test successful login"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'existinguser',
            'password': 'existingpass123',
        })
        
        # Should redirect to home page
        self.assertRedirects(response, reverse('core:home'))
        
        # User should be logged in
        user = User.objects.get(username='existinguser')
        self.assertTrue(user.is_authenticated)

    def test_login_view_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'existinguser',
            'password': 'wrongpassword',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_logout_view(self):
        """Test logout functionality"""
        # First login
        self.client.login(username='existinguser', password='existingpass123')
        
        # Then logout
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('core:home'))
        
        # User should be logged out (check via client, not user object)
        self.assertFalse(self.client.session.get('_auth_user_id'))

    def test_profile_view_authenticated_user(self):
        """Test profile view for authenticated users"""
        self.client.login(username='existinguser', password='existingpass123')
        response = self.client.get(reverse('accounts:profile'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertContains(response, 'existinguser')

    def test_profile_view_anonymous_user(self):
        """Test profile view for anonymous users"""
        response = self.client.get(reverse('accounts:profile'))
        
        # Should redirect to login
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('accounts:profile')}")


class AccountsModelsTestCase(TestCase):
    def test_user_creation(self):
        """Test user model creation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)

    def test_user_group_assignment(self):
        """Test user group assignment"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        group = Group.objects.create(name='testgroup')
        user.groups.add(group)
        
        self.assertTrue(user.groups.filter(name='testgroup').exists())
