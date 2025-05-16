from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from conges.models import Employe

User = get_user_model()

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
        'placeholder': 'Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
        'placeholder': 'Mot de passe'
    }))

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
        'placeholder': 'Email'
    }))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
        'placeholder': 'Prénom'
    }))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
        'placeholder': 'Nom'
    }))
    poste = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
        'placeholder': 'Poste'
    }))
    is_admin = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
    }), label="Administrateur")
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'poste', 'password1', 'password2', 'is_admin')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.is_employee = not self.cleaned_data.get('is_admin')
        user.is_admin = self.cleaned_data.get('is_admin')
        
        if commit:
            user.save()
            
            # Créer le profil employé
            Employe.objects.create(
                user=user,
                nom=self.cleaned_data.get('last_name'),
                prenom=self.cleaned_data.get('first_name'),
                email=self.cleaned_data.get('email'),
                poste=self.cleaned_data.get('poste')
            )
            
        return user

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
        'placeholder': 'Email'
    }))

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
        'placeholder': 'Nouveau mot de passe'
    }))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
        'placeholder': 'Confirmer le mot de passe'
    }))