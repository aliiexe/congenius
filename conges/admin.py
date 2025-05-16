from django.contrib import admin
from .models import TypeConge, Employe, Conge

@admin.register(TypeConge)
class TypeCongeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'est_paye', 'duree_max')
    search_fields = ('nom',)
    list_filter = ('est_paye',)

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'poste')
    search_fields = ('nom', 'prenom', 'email')
    list_filter = ('poste',)

@admin.register(Conge)
class CongeAdmin(admin.ModelAdmin):
    list_display = ('employe', 'type_conge', 'date_debut', 'date_fin', 'statut', 'date_demande')
    list_filter = ('statut', 'type_conge', 'date_demande')
    search_fields = ('employe__nom', 'employe__prenom', 'motif')
    date_hierarchy = 'date_demande'
    readonly_fields = ('date_demande',)