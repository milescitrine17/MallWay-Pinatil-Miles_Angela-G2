from django.urls import path
from . import views

urlpatterns = [
    # Account & Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    # Profile Management
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),

    # Core Feature - Customer Directory
    path('directory/', views.directory_view, name='directory'),
    path('directory/<int:destination_id>/', views.destination_detail_view, name='destination_detail'),

    # Core Feature - Admin Directory Management (CRUD)
    path('admin-panel/directory/', views.admin_directory_view, name='admin_directory'),
    path('admin-panel/directory/create/', views.destination_create_view, name='destination_create'),
    path('admin-panel/directory/<int:destination_id>/edit/', views.destination_edit_view, name='destination_edit'),
    path('admin-panel/directory/<int:destination_id>/delete/', views.destination_delete_view, name='destination_delete'),
    path('admin-panel/directory/<int:destination_id>/archive/', views.destination_archive_view, name='destination_archive'),
    path('admin-panel/directory/<int:destination_id>/featured/', views.destination_toggle_featured_view, name='destination_toggle_featured'),
]
