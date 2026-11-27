from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import Profile, Destination
from .forms import RegistrationForm, ProfileUpdateForm, DestinationForm


def get_user_profile(user):
    """Safely retrieve or create the user profile with appropriate role."""
    default_role = 'admin' if (user.is_superuser or user.is_staff) else 'customer'
    profile, _ = Profile.objects.get_or_create(user=user, defaults={'role': default_role})
    return profile


def _get_owned_destination_or_403(request, destination_id):
    """
    Fetch destination via get_object_or_404 and verify ownership.
    Superusers can manage all records; regular admins may only manage records they created.
    """
    destination = get_object_or_404(
        Destination.objects.select_related('created_by'),
        id=destination_id,
    )
    if not request.user.is_superuser and destination.created_by != request.user:
        raise PermissionDenied(
            "You do not have permission to view or modify another administrator's destination record."
        )
    return destination


def register_view(request):
    """Account Registration view with validation and role assignment."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role_display = user.profile.get_role_display()
            messages.success(
                request,
                f"Your MallWay account ({role_display}) was created successfully! Please log in with your credentials."
            )
            return redirect('login')
        else:
            messages.error(
                request,
                "Registration failed. Please correct the highlighted errors below."
            )
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Login view supporting authentication via either Username or Email."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username_or_email, password=password)

        if user is None and '@' in username_or_email:
            matched_user = User.objects.filter(email__iexact=username_or_email).first()
            if matched_user:
                user = authenticate(request, username=matched_user.username, password=password)

        if user is not None:
            login(request, user)
            profile = get_user_profile(user)
            messages.success(
                request,
                f"Welcome, {user.first_name or user.username}! Logged in as {profile.get_role_display()}."
            )

            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)

            return redirect('dashboard')
        else:
            messages.error(
                request,
                "Invalid username/email or password. Please verify your credentials and try again."
            )
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'next': next_url
    })


def logout_view(request):
    """Logout view that ends the user's session and provides feedback."""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have been logged out successfully. Have a great day!")
    return redirect('login')


@login_required(login_url='login')
def dashboard_view(request):
    """Role-based router that forwards users to their designated dashboard."""
    profile = get_user_profile(request.user)

    if profile.role == 'admin':
        return redirect('admin_dashboard')
    return redirect('customer_dashboard')


@login_required(login_url='login')
def customer_dashboard(request):
    """
    Customer Dashboard view.
    Strictly forbids access by non-customer accounts.
    """
    profile = get_user_profile(request.user)

    if profile.role != 'customer':
        messages.error(
            request,
            "Access Denied: You do not have permission to view the Customer Dashboard as a Mall Administrator."
        )
        return redirect('admin_dashboard')

    featured = Destination.objects.select_related('created_by').filter(
        archived=False, featured=True
    )[:6]
    total_active = Destination.objects.filter(archived=False).count()

    featured_stores = [
        {'name': 'Starlight Fashion Co.', 'category': 'Apparel & Accessories', 'floor': 'Level 2 - Unit 204', 'status': 'Open Now', 'rating': 4.8},
        {'name': 'Bistro De Manila', 'category': 'Dining & Café', 'floor': 'Level 3 - Food Hall', 'status': 'Open Now', 'rating': 4.7},
        {'name': 'CyberWave Tech Hub', 'category': 'Tech & Electronics', 'floor': 'Level 1 - Unit 112', 'status': 'Open Now', 'rating': 4.9},
        {'name': 'CineMax Luxe Theaters', 'category': 'Entertainment & Cinema', 'floor': 'Level 4 - Sky Level', 'status': 'Open Now', 'rating': 4.6},
        {'name': 'The Green Oasis Spa', 'category': 'Wellness & Care', 'floor': 'Level 2 - Unit 218', 'status': 'Open Now', 'rating': 4.8},
        {'name': 'Apex Sports Gear', 'category': 'Sporting Goods', 'floor': 'Level 1 - Unit 105', 'status': 'Open Now', 'rating': 4.5},
    ]

    promotions = [
        {'title': 'Weekend Grand Food Carnival', 'discount': 'Free Drink with Any Meal', 'desc': 'Enjoy complimentary drinks at the Level 3 Dining Loft.', 'badge': 'Dining'},
        {'title': 'MallWay Rewards 2X Points', 'discount': 'Double Points', 'desc': 'Earn 2x loyalty points on all purchases made via registered stores.', 'badge': 'Loyalty'},
    ]

    amenities = [
        {'name': 'Free High-Speed Wi-Fi', 'location': 'Mall-wide network: MallWay-Guest', 'icon': 'wifi'},
        {'name': 'Valet & Covered Parking', 'location': 'Basement 1 & 2 (1,200 slots available)', 'icon': 'car'},
        {'name': 'Customer Information Desk', 'location': 'Ground Floor Main Atrium', 'icon': 'info'},
        {'name': 'ATM & Banking Center', 'location': 'Level 1 Near South Wing Exit', 'icon': 'credit-card'},
        {'name': 'Family Lounge & Baby Care', 'location': 'Level 2 Next to Restrooms', 'icon': 'users'},
    ]

    context = {
        'profile': profile,
        'featured': featured,
        'featured_stores': featured_stores,
        'total_active': total_active,
        'promotions': promotions,
        'amenities': amenities,
    }
    return render(request, 'accounts/customer_dashboard.html', context)


@login_required(login_url='login')
def admin_dashboard(request):
    """
    Mall Administrator Dashboard view.
    Strictly forbids access by non-admin accounts.
    """
    profile = get_user_profile(request.user)

    if profile.role != 'admin':
        messages.error(
            request,
            "Access Denied: You do not have administrator permissions to access the Mall Administrator Dashboard."
        )
        return redirect('customer_dashboard')

    scoped_qs = Destination.objects.all() if request.user.is_superuser else Destination.objects.filter(created_by=request.user)
    total_destinations = scoped_qs.filter(archived=False).count()
    featured_count = scoped_qs.filter(archived=False, featured=True).count()
    archived_count = scoped_qs.filter(archived=True).count()
    registered_users_count = User.objects.count()

    kpi_stats = {
        'total_stores': total_destinations,
        'occupancy_rate': f"{featured_count} Featured",
        'daily_visitors': '4,850',
        'registered_accounts': registered_users_count,
    }

    tenants = [
        {'id': 'ST-101', 'name': 'Starlight Fashion Co.', 'category': 'Fashion', 'unit': 'Level 2 - Unit 204', 'lease_status': 'Active', 'contact': 'mgr@starlight.ph'},
        {'id': 'ST-102', 'name': 'Bistro De Manila', 'category': 'Dining', 'unit': 'Level 3 - Food Hall', 'lease_status': 'Active', 'contact': 'dining@bistromnl.com'},
        {'id': 'ST-103', 'name': 'CyberWave Tech Hub', 'category': 'Electronics', 'unit': 'Level 1 - Unit 112', 'lease_status': 'Active', 'contact': 'support@cyberwave.ph'},
        {'id': 'ST-104', 'name': 'CineMax Luxe Theaters', 'category': 'Entertainment', 'unit': 'Level 4 - Sky Level', 'lease_status': 'Active', 'contact': 'admin@cinemax.com'},
        {'id': 'ST-105', 'name': 'The Green Oasis Spa', 'category': 'Wellness', 'unit': 'Level 2 - Unit 218', 'lease_status': 'Renewal Pending', 'contact': 'oasis@spa.ph'},
        {'id': 'ST-106', 'name': 'Apex Sports Gear', 'category': 'Athletics', 'unit': 'Level 1 - Unit 105', 'lease_status': 'Active', 'contact': 'store@apexsports.ph'},
    ]

    recent_announcements = [
        {'title': 'Annual Fire Safety Inspection Scheduled', 'target': 'All Mall Tenants', 'date': 'Today, 08:30 AM', 'status': 'Broadcasted'},
        {'title': 'Extended Mall Hours for Holiday Shopping', 'target': 'Public & Tenants', 'date': 'Yesterday', 'status': 'Scheduled'},
        {'title': 'Air Conditioning Maintenance - Level 3 Food Loft', 'target': 'Food Loft Tenants', 'date': 'Nov 14, 2026', 'status': 'Completed'},
    ]

    context = {
        'profile': profile,
        'total_destinations': total_destinations,
        'featured_count': featured_count,
        'archived_count': archived_count,
        'kpi_stats': kpi_stats,
        'tenants': tenants,
        'recent_announcements': recent_announcements,
        'registered_users_count': registered_users_count,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required(login_url='login')
def profile_view(request):
    """User Profile View. Logged-in users can view their own profile information."""
    profile = get_user_profile(request.user)
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'profile': profile,
    })


@login_required(login_url='login')
def profile_edit_view(request):
    """User Profile Update View. Logged-in users can update their own details."""
    profile = get_user_profile(request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please check the form below and correct any validation errors.")
    else:
        form = ProfileUpdateForm(user=request.user)

    return render(request, 'accounts/profile_edit.html', {
        'form': form,
        'profile': profile,
    })


# ─── Customer Directory Views ─────────────────────────────────────────────────

@login_required(login_url='login')
def directory_view(request):
    """Customer: browse, search, and filter active destinations."""
    profile = get_user_profile(request.user)
    if profile.role != 'customer':
        messages.error(request, "Access Denied: Switch to a Customer account to use the shopper directory.")
        return redirect('dashboard')

    base_qs = Destination.objects.select_related('created_by').filter(archived=False)
    destinations = base_qs

    search_query = request.GET.get('search', '').strip()
    category = request.GET.get('category', '').strip()
    floor_filter = request.GET.get('floor', '').strip()

    if search_query:
        destinations = destinations.filter(name__icontains=search_query)

    if category:
        valid_categories = {c[0] for c in Destination.CATEGORY_CHOICES}
        if category in valid_categories:
            destinations = destinations.filter(category=category)

    if floor_filter:
        destinations = destinations.filter(floor__icontains=floor_filter)

    featured = base_qs.filter(featured=True)
    floors = base_qs.values_list('floor', flat=True).distinct().order_by('floor')

    return render(
        request,
        'accounts/directory.html',
        {
            'destinations': destinations,
            'search_query': search_query,
            'selected_category': category,
            'selected_floor': floor_filter,
            'category_choices': Destination.CATEGORY_CHOICES,
            'featured': featured,
            'floors': floors,
            'total_count': destinations.count(),
        }
    )


@login_required(login_url='login')
def destination_detail_view(request, destination_id):
    """Customer: view full details of an active destination."""
    profile = get_user_profile(request.user)
    if profile.role != 'customer':
        messages.error(request, "Access Denied: Switch to a Customer account to view shopper destination details.")
        return redirect('dashboard')

    destination = get_object_or_404(
        Destination.objects.select_related('created_by'),
        id=destination_id,
        archived=False,
    )

    return render(
        request,
        'accounts/destination_detail.html',
        {
            'destination': destination,
        }
    )


# ─── Admin Directory Management Views ────────────────────────────────────────

@login_required(login_url='login')
def admin_directory_view(request):
    """Admin: list owned destinations (or all for superuser) with search/filter."""
    profile = get_user_profile(request.user)
    if profile.role != 'admin':
        messages.error(request, 'Access Denied: Mall Administrator privileges required.')
        return redirect('dashboard')

    base_qs = Destination.objects.select_related('created_by')
    if not request.user.is_superuser:
        base_qs = base_qs.filter(created_by=request.user)

    destinations = base_qs

    search_query = request.GET.get('search', '').strip()
    category = request.GET.get('category', '').strip()
    status_filter = request.GET.get('status', '').strip()

    if search_query:
        destinations = destinations.filter(name__icontains=search_query)

    if category:
        valid_categories = {c[0] for c in Destination.CATEGORY_CHOICES}
        if category in valid_categories:
            destinations = destinations.filter(category=category)

    if status_filter == 'active':
        destinations = destinations.filter(archived=False)
    elif status_filter == 'archived':
        destinations = destinations.filter(archived=True)
    elif status_filter == 'featured':
        destinations = destinations.filter(featured=True, archived=False)

    total = base_qs.count()
    active_count = base_qs.filter(archived=False).count()
    archived_count = base_qs.filter(archived=True).count()
    featured_count = base_qs.filter(featured=True, archived=False).count()

    return render(
        request,
        'accounts/admin_directory.html',
        {
            'destinations': destinations,
            'search_query': search_query,
            'selected_category': category,
            'selected_status': status_filter,
            'category_choices': Destination.CATEGORY_CHOICES,
            'total': total,
            'active_count': active_count,
            'archived_count': archived_count,
            'featured_count': featured_count,
        }
    )


@login_required(login_url='login')
def destination_create_view(request):
    """Admin: create a new destination with atomic persistence and validation."""
    profile = get_user_profile(request.user)
    if profile.role != 'admin':
        messages.error(request, 'Access Denied: Mall Administrator privileges required.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                with transaction.atomic():
                    destination = form.save(commit=False)
                    destination.created_by = request.user
                    destination.save()
                messages.success(
                    request,
                    f'Destination "{destination.name}" has been created successfully!'
                )
                return redirect('admin_directory')
            except IntegrityError:
                messages.error(
                    request,
                    'A destination with that exact name, floor, and location already exists.'
                )
        else:
            messages.error(request, "Please check the form and correct the errors below.")
    else:
        form = DestinationForm()

    return render(
        request,
        'accounts/destination_form.html',
        {
            'form': form,
            'form_title': 'Add New Destination',
            'form_action': 'Create Destination',
            'is_edit': False,
        }
    )


@login_required(login_url='login')
def destination_edit_view(request, destination_id):
    """Admin: edit an owned destination."""
    profile = get_user_profile(request.user)
    if profile.role != 'admin':
        messages.error(request, 'Access Denied: Mall Administrator privileges required.')
        return redirect('dashboard')

    destination = _get_owned_destination_or_403(request, destination_id)

    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES, instance=destination)

        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                messages.success(
                    request,
                    f'Destination "{destination.name}" has been updated successfully!'
                )
                return redirect('admin_directory')
            except IntegrityError:
                messages.error(
                    request,
                    'Update failed because another destination already uses that name, floor, and location.'
                )
        else:
            messages.error(request, "Please check the form and correct the errors below.")
    else:
        form = DestinationForm(instance=destination)

    return render(
        request,
        'accounts/destination_form.html',
        {
            'form': form,
            'destination': destination,
            'form_title': f'Edit — {destination.name}',
            'form_action': 'Save Changes',
            'is_edit': True,
        }
    )


@login_required(login_url='login')
def destination_delete_view(request, destination_id):
    """Admin: permanently delete an owned destination (GET shows confirmation, POST deletes)."""
    profile = get_user_profile(request.user)
    if profile.role != 'admin':
        messages.error(request, 'Access Denied: Mall Administrator privileges required.')
        return redirect('dashboard')

    destination = _get_owned_destination_or_403(request, destination_id)

    if request.method == 'POST':
        with transaction.atomic():
            name = destination.name
            destination.delete()

        messages.success(
            request,
            f'Destination "{name}" has been permanently deleted.'
        )
        return redirect('admin_directory')

    return render(
        request,
        'accounts/destination_delete.html',
        {
            'destination': destination,
        }
    )


@login_required(login_url='login')
def destination_archive_view(request, destination_id):
    """Admin: archive (soft-delete) or restore an owned destination."""
    profile = get_user_profile(request.user)
    if profile.role != 'admin':
        messages.error(request, 'Access Denied: Mall Administrator privileges required.')
        return redirect('dashboard')

    destination = _get_owned_destination_or_403(request, destination_id)

    if request.method == 'POST':
        # Business rule: prevent restoring if another active destination now occupies the same floor & location
        if destination.archived:
            conflict = Destination.objects.filter(
                floor__iexact=destination.floor,
                location__iexact=destination.location,
                archived=False,
            ).exclude(pk=destination.pk).first()
            if conflict:
                messages.error(
                    request,
                    f'Cannot restore "{destination.name}": "{conflict.name}" currently occupies {destination.floor} ({destination.location}).'
                )
                return redirect('admin_directory')

        with transaction.atomic():
            destination.archived = not destination.archived
            destination.save()

        if destination.archived:
            messages.success(request, f'Destination "{destination.name}" has been archived.')
        else:
            messages.success(request, f'Destination "{destination.name}" has been restored to the active directory.')

        return redirect('admin_directory')

    return render(
        request,
        'accounts/destination_archive.html',
        {
            'destination': destination,
        }
    )


@login_required(login_url='login')
@require_POST
def destination_toggle_featured_view(request, destination_id):
    """Admin: toggle featured status of an owned destination (POST only)."""
    profile = get_user_profile(request.user)
    if profile.role != 'admin':
        messages.error(request, 'Access Denied: Mall Administrator privileges required.')
        return redirect('dashboard')

    destination = _get_owned_destination_or_403(request, destination_id)

    with transaction.atomic():
        destination.featured = not destination.featured
        destination.save()

    if destination.featured:
        messages.success(request, f'Destination "{destination.name}" is now featured.')
    else:
        messages.success(request, f'Destination "{destination.name}" is no longer featured.')

    return redirect('admin_directory')


# ─── Custom Error Views ──────────────────────────────────────────────────────

def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)


def custom_403_view(request, exception=None):
    return render(request, '403.html', {'error_message': str(exception) if exception else ''}, status=403)


def custom_500_view(request):
    return render(request, '500.html', status=500)
