from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import *
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Conge, Contact, TypeConge, Employe
from .forms import ContactForm, DemandeCongeForm, TraitementCongeForm, TypeCongeForm
import django_filters
from django.http import HttpRequest

from django.db.models.functions import ExtractDay, Cast
from django.db.models import F, IntegerField
from django.db.models import Count, Sum
import json

User = get_user_model()

class CongeFilter(django_filters.FilterSet):
    statut = django_filters.ChoiceFilter(choices=Conge.STATUT_CHOICES)
    date_debut = django_filters.DateFilter(lookup_expr='gte')
    date_fin = django_filters.DateFilter(lookup_expr='lte')
    
    class Meta:
        model = Conge
        fields = ['statut', 'type_conge', 'date_debut', 'date_fin']

def is_admin(user):
    return user.is_admin or user.groups.filter(name='Administrateurs').exists()

def is_employee(user):
    return user.is_employee or user.groups.filter(name='Employés').exists()

@login_required
@user_passes_test(is_employee)
def dashboard_employe(request):
    try:
        employe = request.user.employe_profile
        conges = Conge.objects.filter(employe=employe).order_by('-date_demande')
        
        context = {
            'employe': employe,
            'conges': conges,
            'conges_en_attente': conges.filter(statut='En attente').count(),
            'conges_approuves': conges.filter(statut='Approuvé').count(),
            'conges_rejetes': conges.filter(statut='Rejeté').count(),
        }
        return render(request, 'conges/dashboard_employe.html', context)
    except Employe.DoesNotExist:
        messages.error(request, "Profil employé non trouvé. Veuillez contacter un administrateur.")
        return redirect('home')

@login_required
@user_passes_test(is_employee)
def demande_conge(request):
    try:
        employe = request.user.employe_profile
        
        if request.method == 'POST':
            form = DemandeCongeForm(request.POST)
            if form.is_valid():
                conge = form.save(commit=False)
                conge.employe = employe
                conge.save()
                
                admins = [user.email for user in User.objects.filter(is_admin=True)]
                if admins:
                    send_mail(
                        'Nouvelle demande de congé',
                        f'Une nouvelle demande de congé a été soumise par {employe.prenom} {employe.nom}.',
                        'alibusinessbourak@gmail.com',
                        admins,
                        fail_silently=True,
                    )
                
                messages.success(request, "Votre demande de congé a été soumise avec succès.")
                return redirect('dashboard_employe')
        else:
            form = DemandeCongeForm()
        
        context = {
            'form': form,
            'types_conge': TypeConge.objects.all(),
        }
        return render(request, 'conges/demande_conge.html', context)
    except Employe.DoesNotExist:
        messages.error(request, "Profil employé non trouvé. Veuillez contacter un administrateur.")
        return redirect('home')

@login_required
@user_passes_test(is_employee)
def historique_conges(request):
    try:
        employe = request.user.employe_profile
        conges = Conge.objects.filter(employe=employe).order_by('-date_demande')
        
        conge_filter = CongeFilter(request.GET, queryset=conges)
        
        context = {
            'filter': conge_filter,
            'conges': conge_filter.qs,
        }
        return render(request, 'conges/historique_conges.html', context)
    except Employe.DoesNotExist:
        messages.error(request, "Profil employé non trouvé. Veuillez contacter un administrateur.")
        return redirect('home')

from django.db.models.functions import ExtractDay, Cast
from django.db.models import F, IntegerField, ExpressionWrapper, DurationField, DateField

@login_required
@user_passes_test(is_admin)
def dashboard_admin(request):
    conges = Conge.objects.all().order_by('-date_demande')
    
    # Calcul des statistiques par employé avec calcul de la durée
    employes_stats = (
        Conge.objects
        .values('employe__prenom', 'employe__nom')
        .annotate(
            total_jours=ExpressionWrapper(
                F('date_fin') - F('date_debut'),
                output_field=DurationField()
            )
        )
        .order_by('-total_jours')[:5]
    )
    
    # Préparation des données pour les graphiques
    employes_labels = []
    employes_data = []
    for stat in employes_stats:
        employes_labels.append(f"{stat['employe__prenom']} {stat['employe__nom']}")
        # Convertir la durée en jours en ajoutant 1 pour inclure le jour de début
        duree = stat['total_jours']
        jours = duree.days + 1 if duree else 0
        employes_data.append(jours)

    # Calcul des statistiques par type de congé
    types_stats = (
        Conge.objects
        .values('type_conge__nom')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    
    context = {
        'conges': conges,
        'conges_en_attente': conges.filter(statut='En attente').count(),
        'conges_approuves': conges.filter(statut='Approuvé').count(),
        'conges_rejetes': conges.filter(statut='Rejeté').count(),
        'employes': Employe.objects.count(),
        'employes_labels': json.dumps(employes_labels),
        'employes_data': json.dumps(employes_data),
        'types_conges_labels': json.dumps([t['type_conge__nom'] for t in types_stats]),
        'types_conges_data': json.dumps([t['total'] for t in types_stats])
    }
    
    return render(request, 'conges/dashboard_admin.html', context)

@login_required
@user_passes_test(is_admin)
def gestion_conges(request):
    conges = Conge.objects.all().order_by('-date_demande')
    
    conge_filter = CongeFilter(request.GET, queryset=conges)
    
    context = {
        'filter': conge_filter,
        'conges': conge_filter.qs,
    }
    return render(request, 'conges/gestion_conges.html', context)

@login_required
@user_passes_test(is_admin)
def traitement_conge(request, conge_id):
    conge = get_object_or_404(Conge, id=conge_id)
    
    if request.method == 'POST':
        form = TraitementCongeForm(request.POST, instance=conge)
        if form.is_valid():
            ancien_statut = conge.statut
            conge = form.save(commit=False)
            
            if ancien_statut != conge.statut:
                conge.date_traitement = timezone.now()
            
            conge.save()
            
            send_mail(
                f'Mise à jour de votre demande de congé',
                f'Votre demande de congé du {conge.date_debut} au {conge.date_fin} a été {conge.statut.lower()}.\n\n'
                f'Commentaire: {conge.commentaire_admin}',
                'alibusinessbourak@gmail.com',
                [conge.employe.email],
                fail_silently=True,
            )
            
            messages.success(request, f"La demande de congé a été {conge.statut.lower()} avec succès.")
            return redirect('gestion_conges')
    else:
        form = TraitementCongeForm(instance=conge)
    
    context = {
        'form': form,
        'conge': conge,
    }
    return render(request, 'conges/traitement_conge.html', context)

@login_required
@user_passes_test(is_admin)
def gestion_types_conge(request):
    types_conge = TypeConge.objects.all()
    
    context = {
        'types_conge': types_conge,
    }
    return render(request, 'conges/gestion_types_conge.html', context)

@login_required
@user_passes_test(is_admin)
def ajouter_type_conge(request):
    if request.method == 'POST':
        form = TypeCongeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Le type de congé a été ajouté avec succès.")
            return redirect('gestion_types_conge')
    else:
        form = TypeCongeForm()
    
    context = {
        'form': form,
        'action': 'Ajouter',
    }
    return render(request, 'conges/form_type_conge.html', context)

@login_required
@user_passes_test(is_admin)
def modifier_type_conge(request, type_id):
    type_conge = get_object_or_404(TypeConge, id=type_id)
    
    if request.method == 'POST':
        form = TypeCongeForm(request.POST, instance=type_conge)
        if form.is_valid():
            form.save()
            messages.success(request, "Le type de congé a été modifié avec succès.")
            return redirect('gestion_types_conge')
    else:
        form = TypeCongeForm(instance=type_conge)
    
    context = {
        'form': form,
        'action': 'Modifier',
    }
    return render(request, 'conges/form_type_conge.html', context)

@login_required
@user_passes_test(is_admin)
def supprimer_type_conge(request, type_id):
    type_conge = get_object_or_404(TypeConge, id=type_id)
    
    if request.method == 'POST':
        type_conge.delete()
        messages.success(request, "Le type de congé a été supprimé avec succès.")
        return redirect('gestion_types_conge')
    
    context = {
        'type_conge': type_conge,
    }
    return render(request, 'conges/confirmer_suppression_type_conge.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('login')

# def contactUs(request):
#     if request.method == 'POST':
#         form = ContactForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Votre message a été envoyé avec succès.")
#             return redirect('home')
#     else:
#         form = ContactForm()
    
#     return render(request, 'contact.html', {'form': form})

# def messages(request):
#     messages = Contact.objects.all()
#     return render(request, 'messages.html', {'messages': messages})