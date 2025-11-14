# app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Event
from .models import Festival
from django.contrib.auth.forms import UserChangeForm

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control shadow-sm'}),
            'email': forms.EmailInput(attrs={'class': 'form-control shadow-sm'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control shadow-sm'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control shadow-sm'}),
        }
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'date','time','location', 'description', 'image' ,'entry_fee']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-lg shadow-sm', 'placeholder': 'Enter event name'}),
            'date': forms.DateInput(attrs={'class': 'form-control form-control-lg shadow-sm', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control','type':'time'}),
            'location': forms.TextInput(attrs={'class': 'form-control form-control-lg shadow-sm', 'placeholder': 'Enter location'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-lg shadow-sm', 'rows': 4, 'placeholder': 'Write about the event...'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control form-control-lg'}),
            'entry_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            
        }

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)



class FestivalForm(forms.ModelForm):
    class Meta:
        model = Festival
        fields = ['name', 'description', 'date', 'location', 'organizer', 'image']



class ProfileUpdateForm(UserChangeForm):
    password = None  # Hide password field

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
        }