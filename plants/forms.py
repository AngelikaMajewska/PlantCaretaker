from django import forms
from .models import Plant, Event, OwnedPlants, Watering, UserLocation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = ['name', 'description', 'soil', 'light', 'watering_frequency', 'image']

        def clean_image(self):
            image = self.cleaned_data.get('image')
            if image and not image.content_type.startswith('image/'):
                raise forms.ValidationError("Only image files are allowed.")
            return image


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

        def clean_email(self):
            email = self.cleaned_data['email']
            if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
                raise forms.ValidationError("This email is already in use.")
            return email

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['plant', 'date', 'name', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'datepicker', 'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['plant'].queryset = Plant.objects.filter(ownedplants__owner=user)

# class WateringForm(forms.ModelForm):
#     class Meta:
#         model = Watering
#         fields = ['plant', 'fertiliser']  # Usuń 'user'
#
#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user', None)
#         super().__init__(*args, **kwargs)
#         if user:
#             self.fields['plant'].queryset = Plant.objects.filter(ownedplants__owner=user)

from django import forms
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

class UserLocationForm(forms.ModelForm):
    class Meta:
        model = UserLocation
        fields = ['country', 'city']
        widgets = {
            'country': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
        }