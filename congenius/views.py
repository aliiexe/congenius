from django.db.models import Count
from django.shortcuts import render
from accounts.models import User
from conges.models import Conge

def get_statistics():
    total_users = User.objects.count()
    total_conges = Conge.objects.count()
    
    # Calcul du taux de satisfaction (basé sur les congés approuvés)
    approuves = Conge.objects.filter(statut='Approuvé').count()
    taux_satisfaction = int((approuves / total_conges * 100) if total_conges > 0 else 0)
    
    # Calcul du gain de temps moyen (estimation)
    gain_temps = 50  # Valeur fixe pour l'exemple, à adapter selon vos besoins
    
    # Disponibilité système (24/7)
    disponibilite = "24/7"
    
    # Nombre total d'utilisateurs
    nb_utilisateurs = f"{total_users}+"
    
    return {
        'satisfaction': f"{taux_satisfaction}%",
        'gain_temps': f"{gain_temps}%",
        'disponibilite': disponibilite,
        'utilisateurs': nb_utilisateurs
    }

def home(request):
    context = {
        'stats': get_statistics()
    }
    return render(request, '/templates/home.html', context)