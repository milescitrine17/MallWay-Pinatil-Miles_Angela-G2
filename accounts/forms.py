import os
import re
from PIL import Image, UnidentifiedImageError
from django import forms
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Destination


MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
PHONE_PATTERN = re.compile(r'^[+\d\s\-()]{5,20}$')


def validate_uploaded_image(uploaded_file):
    """Verify uploaded image size, extension, and file contents."""
    if not uploaded_file:
        return uploaded_file

    if uploaded_file.size > MAX_IMAGE_SIZE_BYTES:
        raise forms.ValidationError("Image file size must not exceed 5 MB.")

    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise forms.ValidationError(
            "Unsupported image format. Allowed formats: JPG, JPEG, PNG, GIF, WEBP."
        )

    try:
        img = Image.open(uploaded_file)
        img.verify()
        uploaded_file.seek(0)
    except (UnidentifiedImageError, Exception):
        raise forms.ValidationError("The uploaded file is not a valid or readable image.")

    return uploaded_file


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="First Name",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter first name',
            'class': 'form-input',
            'autocomplete': 'given-name'
        })
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Last Name",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter last name',
            'class': 'form-input',
            'autocomplete': 'family-name'
        })
    )

    email = forms.EmailField(
        required=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'placeholder': 'you@example.com',
            'class': 'form-input',
            'autocomplete': 'email'
        })
    )

    contact_number = forms.CharField(
        max_length=20,
        required=True,
        label="Contact Number",
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. +63 912 345 6789',
            'class': 'form-input',
            'autocomplete': 'tel'
        })
    )

    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        required=True,
        label="Account Role",
        initial='customer',
        widget=forms.Select(attrs={'class': 'form-input'}),
        help_text="Select your role to access the corresponding dashboard features."
    )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'contact_number',
            'role',
            'password1',
            'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Choose a unique username',
            'class': 'form-input',
            'autocomplete': 'username'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Create a strong password',
            'class': 'form-input',
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Re-enter your password to confirm',
            'class': 'form-input',
            'autocomplete': 'new-password'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists. Please use a different email or log in."
            )
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                "This username is already taken. Please choose another username."
            )
        return username

    def clean_contact_number(self):
        contact = self.cleaned_data.get('contact_number', '').strip()
        if contact and not PHONE_PATTERN.match(contact):
            raise forms.ValidationError(
                "Enter a valid contact number (5-20 digits, spaces, +, -, or parentheses)."
            )
        return contact

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name'].strip()
        user.last_name = self.cleaned_data['last_name'].strip()
        user.email = self.cleaned_data['email'].strip().lower()
        selected_role = self.cleaned_data.get('role', 'customer')
        contact = self.cleaned_data.get('contact_number', '').strip()

        if commit:
            with transaction.atomic():
                user.save()
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.role = selected_role
                profile.contact_number = contact
                profile.save()

        return user


class ProfileUpdateForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="First Name",
        widget=forms.TextInput(attrs={
            'placeholder': 'Your first name',
            'class': 'form-input',
            'autocomplete': 'given-name'
        })
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Last Name",
        widget=forms.TextInput(attrs={
            'placeholder': 'Your last name',
            'class': 'form-input',
            'autocomplete': 'family-name'
        })
    )

    email = forms.EmailField(
        required=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'placeholder': 'your.email@example.com',
            'class': 'form-input',
            'autocomplete': 'email'
        })
    )

    contact_number = forms.CharField(
        max_length=20,
        required=False,
        label="Contact Number",
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. +63 912 345 6789',
            'class': 'form-input',
            'autocomplete': 'tel'
        })
    )

    profile_photo = forms.ImageField(
        required=False,
        label="Profile Photo",
        widget=forms.FileInput(attrs={
            'class': 'form-file-input',
            'accept': 'image/*'
        }),
        help_text="Upload a JPG, PNG, or GIF image (max 5MB recommended)."
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

            if hasattr(user, 'profile'):
                self.fields['contact_number'].initial = user.profile.contact_number

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        query = User.objects.filter(email__iexact=email)
        if self.user:
            query = query.exclude(pk=self.user.pk)
        if query.exists():
            raise forms.ValidationError(
                "This email address is already in use by another account. Please choose a different one."
            )
        return email

    def clean_contact_number(self):
        contact = self.cleaned_data.get('contact_number', '').strip()
        if contact and not PHONE_PATTERN.match(contact):
            raise forms.ValidationError(
                "Enter a valid contact number (5-20 digits, spaces, +, -, or parentheses)."
            )
        return contact

    def clean_profile_photo(self):
        photo = self.cleaned_data.get('profile_photo')
        return validate_uploaded_image(photo)

    def save(self):
        if not self.user:
            return None

        with transaction.atomic():
            self.user.first_name = self.cleaned_data['first_name'].strip()
            self.user.last_name = self.cleaned_data['last_name'].strip()
            self.user.email = self.cleaned_data['email'].strip().lower()
            self.user.save()

            profile, _ = Profile.objects.get_or_create(user=self.user)
            profile.contact_number = self.cleaned_data.get('contact_number', '').strip()

            if self.cleaned_data.get('profile_photo'):
                profile.profile_photo = self.cleaned_data['profile_photo']

            profile.save()
        return self.user


class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = [
            'name',
            'category',
            'description',
            'floor',
            'location',
            'operating_hours',
            'featured',
            'image',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. H&M, Jollibee, Information Desk'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Brief description...', 'rows': 3}),
            'floor': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Ground Floor, Level 2'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Unit 203, East Wing'}),
            'operating_hours': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 10:00 AM - 9:00 PM daily'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'image': forms.FileInput(attrs={'class': 'form-file-input', 'accept': 'image/*'}),
        }
        labels = {
            'name': 'Destination Name',
            'category': 'Category',
            'description': 'Description',
            'floor': 'Floor',
            'location': 'Location / Unit',
            'operating_hours': 'Operating Hours',
            'featured': 'Mark as Featured',
            'image': 'Destination Image',
        }

    def clean_name(self):
        name = ' '.join(self.cleaned_data.get('name', '').split())
        if not name:
            raise forms.ValidationError("Destination name is required.")
        if len(name) < 2:
            raise forms.ValidationError("Destination name must be at least 2 characters long.")
        return name

    def clean_floor(self):
        floor = ' '.join(self.cleaned_data.get('floor', '').split())
        if not floor:
            raise forms.ValidationError("Floor information is required.")
        if len(floor) < 2:
            raise forms.ValidationError("Floor must be at least 2 characters long.")
        return floor

    def clean_location(self):
        location = ' '.join(self.cleaned_data.get('location', '').split())
        if not location:
            raise forms.ValidationError("Location / Unit is required.")
        if len(location) < 2:
            raise forms.ValidationError("Location / Unit must be at least 2 characters long.")
        return location

    def clean_operating_hours(self):
        hours = ' '.join(self.cleaned_data.get('operating_hours', '').split())
        if hours and len(hours) < 3:
            raise forms.ValidationError("Operating hours must be at least 3 characters if specified.")
        return hours

    def clean_description(self):
        return self.cleaned_data.get('description', '').strip()

    def clean_image(self):
        image = self.cleaned_data.get('image')
        # Only validate newly uploaded files (not existing FieldFile references)
        if image and hasattr(image, 'file') and hasattr(image, 'content_type'):
            return validate_uploaded_image(image)
        return image

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        floor = cleaned_data.get('floor')
        location = cleaned_data.get('location')

        if floor and location:
            # Business rule: no two active destinations can occupy the exact same floor & unit/location
            unit_conflict = Destination.objects.filter(
                floor__iexact=floor,
                location__iexact=location,
                archived=False,
            )
            if self.instance and self.instance.pk:
                unit_conflict = unit_conflict.exclude(pk=self.instance.pk)
            if unit_conflict.exists():
                existing = unit_conflict.first()
                raise forms.ValidationError(
                    f'Location conflict: "{existing.name}" already occupies {floor} ({location}). '
                    f'Please assign a different unit/location or archive the existing entry first.'
                )

        if name and floor and location:
            exact_dup = Destination.objects.filter(
                name__iexact=name,
                floor__iexact=floor,
                location__iexact=location,
            )
            if self.instance and self.instance.pk:
                exact_dup = exact_dup.exclude(pk=self.instance.pk)
            if exact_dup.exists():
                raise forms.ValidationError(
                    f'A destination named "{name}" at {floor} ({location}) already exists.'
                )

        return cleaned_data
