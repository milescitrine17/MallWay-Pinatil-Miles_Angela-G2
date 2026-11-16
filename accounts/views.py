from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Profile
from .forms import RegistrationForm, ProfileUpdateForm


def get_user_profile(user):
    """Safely retrieve or create the user profile with appropriate role."""
    default_role = 'admin' if (user.is_superuser or user.is_staff) else 'customer'
    profile, _ = Profile.objects.get_or_create(user=user, defaults={'role': default_role})
    return profile


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

        # Attempt authentication with username directly
        user = authenticate(request, username=username_or_email, password=password)

        # If not authenticated, check if the input corresponds to a unique email
        if user is None and '@' in username_or_email:
            matched_user = User.objects.filter(email__iexact=username_or_email).first()
            if matched_user:
                user = authenticate(request, username=matched_user.username, password=password)

        if user is not None:
            login(request, user)
            profile = get_user_profile(user)
            messages.success(
                request,
                f"Welcome back, {user.first_name or user.username}! Logged in as {profile.get_role_display()}."
            )

            # Redirect safely to next parameter if present
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

    # Mall content tailored for customers
    featured_stores = [
        {'name': 'Starlight Fashion Co.', 'category': 'Apparel & Accessories', 'floor': 'Level 2 - Unit 204', 'status': 'Open Now', 'rating': 4.8},
        {'name': 'Bistro De Manila', 'category': 'Dining & Café', 'floor': 'Level 3 - Food Hall', 'status': 'Open Now', 'rating': 4.9},
        {'name': 'CyberWave Tech Hub', 'category': 'Electronics & Gadgets', 'floor': 'Level 1 - Unit 112', 'status': 'Open Now', 'rating': 4.7},
        {'name': 'CineMax Luxe Theaters', 'category': 'Entertainment & Cinema', 'floor': 'Level 4 - Sky Level', 'status': 'Now Showing', 'rating': 4.9},
        {'name': 'The Green Oasis Spa', 'category': 'Wellness & Beauty', 'floor': 'Level 2 - Unit 218', 'status': 'Open Now', 'rating': 4.6},
        {'name': 'Metro Gourmet Supermarket', 'category': 'Groceries & Daily Essentials', 'floor': 'Lower Ground - LG01', 'status': 'Open Now', 'rating': 4.8},
    ]

    promotions = [
        {'title': 'Summer Grand Opening Sale', 'discount': 'Up to 50% OFF', 'desc': 'Special discounts across over 35 retail partners this weekend.', 'badge': 'Hot Deal'},
        {'title': 'Weekend Food Festival', 'discount': 'Free Drink with Any Meal', 'desc': 'Enjoy complimentary drinks at the Level 3 Dining Loft.', 'badge': 'Dining'},
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
        'featured_stores': featured_stores,
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

    # Content tailored for administrators
    kpi_stats = {
        'total_stores': 52,
        'active_tenants': 48,
        'occupancy_rate': '92.3%',
        'daily_visitors': '4,850',
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

    registered_users_count = User.objects.count()

    context = {
        'profile': profile,
        'kpi_stats': kpi_stats,
        'tenants': tenants,
        'recent_announcements': recent_announcements,
        'registered_users_count': registered_users_count,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required(login_url='login')
def profile_view(request):
    """
    User Profile View.
    Logged-in users can view their own profile information.
    Users can ONLY view their own profile.
    """
    profile = get_user_profile(request.user)

    context = {
        'user': request.user,
        'profile': profile,
    }
    return render(request, 'accounts/profile.html', context)


@login_required(login_url='login')
def profile_edit_view(request):
    """
    User Profile Update View.
    Logged-in users can update their own details (name, email, contact number, profile photo).
    Users can ONLY edit their own profile.
    """
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

    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'accounts/profile_edit.html', context)
