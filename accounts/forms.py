from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Destination


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
        widget=forms.Select(attrs={
            'class': 'form-input'
        }),
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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name'].strip()
        user.last_name = self.cleaned_data['last_name'].strip()
        user.email = self.cleaned_data['email'].strip().lower()
        selected_role = self.cleaned_data.get('role', 'customer')
        contact = self.cleaned_data.get('contact_number', '').strip()

        if commit:
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

    def save(self):
        if not self.user:
            return None

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
            'operating_hours': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 10:00 AM – 9:00 PM daily'}),
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
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Destination name is required.")
        return name

    def clean_floor(self):
        floor = self.cleaned_data.get('floor', '').strip()
        if not floor:
            raise forms.ValidationError("Floor information is required.")
        return floor

    def clean_location(self):
        location = self.cleaned_data.get('location', '').strip()
        if not location:
            raise forms.ValidationError("Location / Unit is required.")
        return location
