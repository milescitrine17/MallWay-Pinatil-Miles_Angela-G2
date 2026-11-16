import tempfile
from PIL import Image
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import Profile, Destination


def get_temporary_image():
    """Generate a valid temporary in-memory image for upload tests."""
    image = Image.new('RGB', (100, 100), color=(73, 109, 137))
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
    image.save(temp_file, format='JPEG')
    temp_file.seek(0)
    return SimpleUploadedFile(
        name='test_avatar.jpg',
        content=temp_file.read(),
        content_type='image/jpeg'
    )


class AccountRegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')

    def test_registration_success_customer(self):
        """Test registering a new customer account with valid data."""
        data = {
            'username': 'john_customer',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'contact_number': '+63 912 345 6789',
            'role': 'customer',
            'password1': 'SecurePass123!@#',
            'password2': 'SecurePass123!@#',
        }
        response = self.client.post(self.register_url, data, follow=True)
        self.assertRedirects(response, reverse('login'))
        self.assertContains(response, 'created successfully')

        # Verify user in database
        user = User.objects.get(username='john_customer')
        self.assertTrue(user.check_password('SecurePass123!@#'))
        self.assertNotEqual(user.password, 'SecurePass123!@#')  # Password must be hashed!
        self.assertEqual(user.email, 'john.doe@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')

        # Verify role and contact number
        self.assertEqual(user.profile.role, 'customer')
        self.assertEqual(user.profile.contact_number, '+63 912 345 6789')

    def test_registration_success_admin(self):
        """Test registering a new administrator account."""
        data = {
            'username': 'admin_sarah',
            'first_name': 'Sarah',
            'last_name': 'Conner',
            'email': 'sarah.admin@mallway.com',
            'contact_number': '+63 999 888 7777',
            'role': 'admin',
            'password1': 'AdminSecret987!#',
            'password2': 'AdminSecret987!#',
        }
        response = self.client.post(self.register_url, data, follow=True)
        self.assertRedirects(response, reverse('login'))

        user = User.objects.get(username='admin_sarah')
        self.assertEqual(user.profile.role, 'admin')

    def test_registration_duplicate_email(self):
        """Test that duplicate email registration is rejected."""
        User.objects.create_user(
            username='existing_user',
            email='duplicate@example.com',
            password='OldPassword123!'
        )

        data = {
            'username': 'new_user_diff',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'duplicate@example.com',
            'contact_number': '1234567890',
            'role': 'customer',
            'password1': 'NewPass123!@#',
            'password2': 'NewPass123!@#',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'email',
            'An account with this email address already exists. Please use a different email or log in.'
        )

    def test_registration_password_mismatch(self):
        """Test that mismatched passwords fail validation."""
        data = {
            'username': 'mismatch_user',
            'first_name': 'Mis',
            'last_name': 'Match',
            'email': 'mismatch@example.com',
            'contact_number': '1234567890',
            'role': 'customer',
            'password1': 'PasswordOne123!',
            'password2': 'PasswordDifferent999!',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].has_error('password2'))

    def test_registration_missing_required_fields(self):
        """Test that omitting required fields prevents submission."""
        data = {
            'username': '',
            'first_name': '',
            'last_name': '',
            'email': 'not-an-email',
            'contact_number': '',
            'password1': '',
            'password2': '',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].has_error('username'))
        self.assertTrue(response.context['form'].has_error('email'))


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

        # Customer account
        self.customer_user = User.objects.create_user(
            username='shopper_dan',
            email='dan@example.com',
            password='DanPassword123!',
            first_name='Dan',
            last_name='Miller'
        )
        self.customer_user.profile.role = 'customer'
        self.customer_user.profile.save()

        # Admin account
        self.admin_user = User.objects.create_user(
            username='admin_clara',
            email='clara@mallway.com',
            password='ClaraPassword123!',
            first_name='Clara',
            last_name='Oswald'
        )
        self.admin_user.profile.role = 'admin'
        self.admin_user.profile.save()

    def test_login_with_username_success(self):
        """Test login using username."""
        response = self.client.post(self.login_url, {
            'username': 'shopper_dan',
            'password': 'DanPassword123!'
        }, follow=True)
        self.assertRedirects(response, reverse('customer_dashboard'))
        self.assertContains(response, 'Welcome, Dan!')

    def test_login_with_email_success(self):
        """Test login using email address."""
        response = self.client.post(self.login_url, {
            'username': 'clara@mallway.com',
            'password': 'ClaraPassword123!'
        }, follow=True)
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertContains(response, 'Mall Operations Console')

    def test_login_invalid_credentials(self):
        """Test login failure on wrong password."""
        response = self.client.post(self.login_url, {
            'username': 'shopper_dan',
            'password': 'WrongPassword999'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username/email or password')

    def test_logout(self):
        """Test user logout ends session."""
        self.client.login(username='shopper_dan', password='DanPassword123!')
        response = self.client.get(self.logout_url, follow=True)
        self.assertRedirects(response, reverse('login'))
        self.assertContains(response, 'logged out successfully')


class RoleBasedDashboardSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.customer = User.objects.create_user(
            username='cust_user',
            email='cust@example.com',
            password='TestPass123!',
            first_name='Customer'
        )
        self.customer.profile.role = 'customer'
        self.customer.profile.save()

        self.admin = User.objects.create_user(
            username='admin_user',
            email='admin@example.com',
            password='TestPass123!',
            first_name='Administrator'
        )
        self.admin.profile.role = 'admin'
        self.admin.profile.save()

    def test_unauthenticated_user_redirected_to_login(self):
        """Test protected pages redirect logged-out users to login."""
        protected_urls = [
            reverse('dashboard'),
            reverse('customer_dashboard'),
            reverse('admin_dashboard'),
            reverse('profile'),
            reverse('profile_edit'),
        ]
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith(reverse('login')))

    def test_customer_can_access_own_dashboard(self):
        """Customer can access customer_dashboard."""
        self.client.login(username='cust_user', password='TestPass123!')
        response = self.client.get(reverse('customer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Shopper Dashboard')

    def test_admin_can_access_own_dashboard(self):
        """Admin can access admin_dashboard."""
        self.client.login(username='admin_user', password='TestPass123!')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mall Operations Console')

    def test_customer_CANNOT_access_admin_dashboard_by_url(self):
        """
        SECURITY REQUIREMENT:
        A customer typing the admin dashboard URL must NOT be allowed to view it.
        They must be redirected with an access denied warning.
        """
        self.client.login(username='cust_user', password='TestPass123!')
        response = self.client.get(reverse('admin_dashboard'), follow=True)
        self.assertRedirects(response, reverse('customer_dashboard'))
        self.assertContains(response, 'Access Denied')

    def test_admin_CANNOT_access_customer_dashboard_by_url(self):
        """
        SECURITY REQUIREMENT:
        An admin typing the customer dashboard URL must NOT view it and is bounced to admin dashboard.
        """
        self.client.login(username='admin_user', password='TestPass123!')
        response = self.client.get(reverse('customer_dashboard'), follow=True)
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertContains(response, 'Access Denied')


class UserProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='profile_user',
            email='profile@example.com',
            password='UserPass123!',
            first_name='Taylor',
            last_name='Swift'
        )
        self.user.profile.role = 'customer'
        self.user.profile.contact_number = '+63 900 111 2233'
        self.user.profile.save()

    def test_user_can_view_own_profile(self):
        """Logged-in user can view their profile information."""
        self.client.login(username='profile_user', password='UserPass123!')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Taylor')
        self.assertContains(response, 'Swift')
        self.assertContains(response, 'profile@example.com')
        self.assertContains(response, '+63 900 111 2233')
        self.assertContains(response, 'Customer')

    def test_user_can_update_profile_details(self):
        """Logged-in user can update their name, email, contact number, and photo."""
        self.client.login(username='profile_user', password='UserPass123!')
        avatar = get_temporary_image()

        data = {
            'first_name': 'Taylor Alison',
            'last_name': 'Swift',
            'email': 'taylor.updated@example.com',
            'contact_number': '+63 999 777 5555',
            'profile_photo': avatar,
        }
        response = self.client.post(reverse('profile_edit'), data, follow=True)
        self.assertRedirects(response, reverse('profile'))
        self.assertContains(response, 'profile details have been updated successfully')

        # Check DB update
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Taylor Alison')
        self.assertEqual(self.user.email, 'taylor.updated@example.com')
        self.assertEqual(self.user.profile.contact_number, '+63 999 777 5555')
        self.assertTrue(bool(self.user.profile.profile_photo))

    def test_profile_update_duplicate_email_rejected(self):
        """User cannot change their email to an address already taken by someone else."""
        User.objects.create_user(
            username='other_user',
            email='taken@example.com',
            password='OtherPass123!'
        )
        self.client.login(username='profile_user', password='UserPass123!')

        data = {
            'first_name': 'Taylor',
            'last_name': 'Swift',
            'email': 'taken@example.com',
            'contact_number': '12345',
        }
        response = self.client.post(reverse('profile_edit'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].has_error('email'))


class MallDirectoryCoreFeatureTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.admin = User.objects.create_user(
            username='dir_admin',
            email='admin@mallway.ph',
            password='AdminPass123!',
            first_name='Admin'
        )
        self.admin.profile.role = 'admin'
        self.admin.profile.save()

        self.customer = User.objects.create_user(
            username='dir_customer',
            email='cust@mallway.ph',
            password='CustomerPass123!',
            first_name='Customer'
        )
        self.customer.profile.role = 'customer'
        self.customer.profile.save()

        self.sample_dest = Destination.objects.create(
            name='Zara Manila',
            category='store',
            description='International fashion retail store.',
            floor='Ground Floor',
            location='Unit G-12, Main Atrium',
            operating_hours='10:00 AM - 9:00 PM',
            featured=True,
            archived=False,
            created_by=self.admin
        )

    def test_admin_can_create_destination(self):
        """Admin can create a new destination through UI form (Create)."""
        self.client.login(username='dir_admin', password='AdminPass123!')
        data = {
            'name': 'Din Tai Fung',
            'category': 'restaurant',
            'description': 'Famous world-class xiao long bao and Taiwanese cuisine.',
            'floor': 'Level 2',
            'location': 'Unit 201, Dining Hub',
            'operating_hours': '11:00 AM - 10:00 PM',
            'featured': True,
        }
        response = self.client.post(reverse('destination_create'), data, follow=True)
        self.assertRedirects(response, reverse('admin_directory'))
        self.assertContains(response, 'created successfully')

        dest = Destination.objects.get(name='Din Tai Fung')
        self.assertEqual(dest.category, 'restaurant')
        self.assertEqual(dest.floor, 'Level 2')
        self.assertEqual(dest.created_by, self.admin)
        self.assertTrue(dest.featured)

    def test_destination_validation_missing_fields(self):
        """Destination creation fails if required fields are missing."""
        self.client.login(username='dir_admin', password='AdminPass123!')
        data = {
            'name': '',
            'category': 'store',
            'floor': '',
            'location': '',
        }
        response = self.client.post(reverse('destination_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].has_error('name'))
        self.assertTrue(response.context['form'].has_error('floor'))
        self.assertTrue(response.context['form'].has_error('location'))

    def test_admin_can_read_directory(self):
        """Admin can view the directory management table (Read)."""
        self.client.login(username='dir_admin', password='AdminPass123!')
        response = self.client.get(reverse('admin_directory'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Zara Manila')
        self.assertContains(response, 'Directory Management')

    def test_admin_can_update_destination(self):
        """Admin can edit an existing destination (Update)."""
        self.client.login(username='dir_admin', password='AdminPass123!')
        data = {
            'name': 'Zara Flagship Manila',
            'category': 'store',
            'description': 'Updated flagship store description.',
            'floor': 'Ground Floor',
            'location': 'Unit G-10 to G-14, North Wing',
            'operating_hours': '10:00 AM - 10:00 PM',
            'featured': False,
        }
        response = self.client.post(
            reverse('destination_edit', args=[self.sample_dest.id]),
            data,
            follow=True
        )
        self.assertRedirects(response, reverse('admin_directory'))
        self.assertContains(response, 'updated successfully')

        self.sample_dest.refresh_from_db()
        self.assertEqual(self.sample_dest.name, 'Zara Flagship Manila')
        self.assertEqual(self.sample_dest.location, 'Unit G-10 to G-14, North Wing')
        self.assertFalse(self.sample_dest.featured)

    def test_admin_can_archive_and_restore_destination(self):
        """Admin can soft-delete (archive) and restore a destination."""
        self.client.login(username='dir_admin', password='AdminPass123!')

        response = self.client.post(
            reverse('destination_archive', args=[self.sample_dest.id]),
            follow=True
        )
        self.assertRedirects(response, reverse('admin_directory'))
        self.sample_dest.refresh_from_db()
        self.assertTrue(self.sample_dest.archived)

        response = self.client.post(
            reverse('destination_archive', args=[self.sample_dest.id]),
            follow=True
        )
        self.assertRedirects(response, reverse('admin_directory'))
        self.sample_dest.refresh_from_db()
        self.assertFalse(self.sample_dest.archived)

    def test_admin_can_delete_destination(self):
        """Admin can permanently delete a destination (Delete)."""
        self.client.login(username='dir_admin', password='AdminPass123!')
        dest_id = self.sample_dest.id
        response = self.client.post(
            reverse('destination_delete', args=[dest_id]),
            follow=True
        )
        self.assertRedirects(response, reverse('admin_directory'))
        self.assertContains(response, 'permanently deleted')
        self.assertFalse(Destination.objects.filter(id=dest_id).exists())

    def test_admin_can_toggle_featured(self):
        """Admin can toggle featured flag on a destination."""
        self.client.login(username='dir_admin', password='AdminPass123!')
        self.assertTrue(self.sample_dest.featured)

        self.client.post(reverse('destination_toggle_featured', args=[self.sample_dest.id]))
        self.sample_dest.refresh_from_db()
        self.assertFalse(self.sample_dest.featured)

    def test_customer_can_browse_directory(self):
        """Customer can access directory and see active destinations (Read)."""
        self.client.login(username='dir_customer', password='CustomerPass123!')
        response = self.client.get(reverse('directory'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Zara Manila')

    def test_customer_cannot_see_archived_destinations(self):
        """Archived destinations are hidden from customer directory view."""
        self.sample_dest.archived = True
        self.sample_dest.save()

        self.client.login(username='dir_customer', password='CustomerPass123!')
        response = self.client.get(reverse('directory'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Zara Manila')

    def test_customer_can_view_destination_detail(self):
        """Customer can view the details page of an active destination."""
        self.client.login(username='dir_customer', password='CustomerPass123!')
        response = self.client.get(reverse('destination_detail', args=[self.sample_dest.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Zara Manila')
        self.assertContains(response, 'International fashion retail store.')
        self.assertContains(response, 'Unit G-12, Main Atrium')

    def test_customer_denied_from_admin_directory_views(self):
        """Customers cannot access admin management views by URL."""
        self.client.login(username='dir_customer', password='CustomerPass123!')
        admin_urls = [
            reverse('admin_directory'),
            reverse('destination_create'),
            reverse('destination_edit', args=[self.sample_dest.id]),
            reverse('destination_delete', args=[self.sample_dest.id]),
            reverse('destination_archive', args=[self.sample_dest.id]),
        ]
        for url in admin_urls:
            response = self.client.get(url, follow=True)
            self.assertRedirects(response, reverse('customer_dashboard'))
            self.assertContains(response, 'Access Denied')

    def test_unauthenticated_user_redirected_to_login(self):
        """Unauthenticated requests to directory views redirect to login."""
        urls = [
            reverse('directory'),
            reverse('destination_detail', args=[self.sample_dest.id]),
            reverse('admin_directory'),
            reverse('destination_create'),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith(reverse('login')))
