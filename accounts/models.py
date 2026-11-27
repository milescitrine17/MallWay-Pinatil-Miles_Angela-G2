from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Mall Administrator'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer'
    )

    contact_number = models.CharField(
        max_length=20,
        blank=True
    )

    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'admin' if (instance.is_superuser or instance.is_staff) else 'customer'
        Profile.objects.get_or_create(user=instance, defaults={'role': role})
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()


class Destination(models.Model):
    CATEGORY_CHOICES = (
        ('store', 'Store'),
        ('restaurant', 'Restaurant'),
        ('facility', 'Facility'),
        ('entrance', 'Entrance'),
        ('other', 'Other'),
    )

    name = models.CharField(
        max_length=150,
        validators=[MinLengthValidator(2, message="Destination name must be at least 2 characters.")]
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )
    description = models.TextField(blank=True)
    floor = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(2, message="Floor must be at least 2 characters.")]
    )
    location = models.CharField(
        max_length=150,
        validators=[MinLengthValidator(2, message="Location / Unit must be at least 2 characters.")]
    )
    operating_hours = models.CharField(max_length=100, blank=True)
    featured = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to='destination_images/',
        blank=True,
        null=True
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='destinations'
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'floor', 'location'],
                name='unique_destination_name_floor_location'
            ),
        ]
        indexes = [
            models.Index(fields=['archived', 'featured'], name='dest_archived_featured_idx'),
        ]

    def __str__(self):
        return self.name

    def get_category_display_icon(self):
        icons = {
            'store': '🛍️',
            'restaurant': '🍽️',
            'facility': '🏢',
            'entrance': '🚪',
            'other': '📍',
        }
        return icons.get(self.category, '📍')
