from django.urls import path
from . import views

urlpatterns = [
    # URLs pour les employés
    path('dashboard/', views.dashboard_employe, name='dashboard_employe'),
    path('demande/', views.demande_conge, name='demande_conge'),
    path('historique/', views.historique_conges, name='historique_conges'),
    
    # URLs pour les administrateurs
    path('admin/dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('admin/gestion/', views.gestion_conges, name='gestion_conges'),
    path('admin/traitement/<int:conge_id>/', views.traitement_conge, name='traitement_conge'),
    path('admin/types/', views.gestion_types_conge, name='gestion_types_conge'),
    path('admin/types/ajouter/', views.ajouter_type_conge, name='ajouter_type_conge'),
    path('admin/types/modifier/<int:type_id>/', views.modifier_type_conge, name='modifier_type_conge'),
    path('admin/types/supprimer/<int:type_id>/', views.supprimer_type_conge, name='supprimer_type_conge'),
    path("logout/", views.logout_view, name="logout"),
    # path("contactUs/", views.contactUs, name="contactUs"),
    # path("messages", views.messages, name="messages"),
]