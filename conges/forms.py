from django import forms
from .models import Conge, Contact, TypeConge
from django.core.exceptions import ValidationError
from django.utils import timezone

class DemandeCongeForm(forms.ModelForm):
    class Meta:
        model = Conge
        fields = ['type_conge', 'date_debut', 'date_fin', 'motif']
        widgets = {
            'type_conge': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'date_debut': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'date'
            }),
            'date_fin': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'date'
            }),
            'motif': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        type_conge = cleaned_data.get('type_conge')
        
        if date_debut and date_fin:
            if date_debut > date_fin:
                raise ValidationError("La date de début doit être antérieure à la date de fin.")
            
            if date_debut < timezone.now().date():
                raise ValidationError("La date de début ne peut pas être dans le passé.")
            
            if type_conge and type_conge.duree_max:
                duree = (date_fin - date_debut).days + 1
                if duree > type_conge.duree_max:
                    raise ValidationError(f"La durée maximale pour ce type de congé est de {type_conge.duree_max} jours.")
        
        return cleaned_data

class TraitementCongeForm(forms.ModelForm):
    class Meta:
        model = Conge
        fields = ['statut', 'commentaire_admin']
        widgets = {
            'statut': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'commentaire_admin': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3
            })
        }

class TypeCongeForm(forms.ModelForm):
    class Meta:
        model = TypeConge
        fields = ['nom', 'description', 'est_paye', 'duree_max']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3
            }),
            'est_paye': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
            }),
            'duree_max': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            })
        }

# class ContactForm(forms.ModelForm):
#     class Meta:
#         model = Contact
#         fields = ['nom', 'message']