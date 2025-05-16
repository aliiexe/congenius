from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

class TypeConge(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    est_paye = models.BooleanField(default=True)
    duree_max = models.PositiveIntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "Type de congé"
        verbose_name_plural = "Types de congé"

class Employe(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employe_profile')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    poste = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"

class Conge(models.Model):
    STATUT_CHOICES = [
        ('En attente', 'En attente'),
        ('Approuvé', 'Approuvé'),
        ('Rejeté', 'Rejeté')
    ]
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='conges')
    type_conge = models.ForeignKey(TypeConge, on_delete=models.SET_NULL, null=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    motif = models.TextField(blank=True)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='En attente')
    date_demande = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    commentaire_admin = models.TextField(blank=True, verbose_name="Commentaire de l'administrateur")
    
    def clean(self):
        if self.date_debut and self.date_fin:
            if self.date_debut > self.date_fin:
                raise ValidationError("La date de début doit être antérieure à la date de fin.")
            
            if self.date_debut < timezone.now().date():
                raise ValidationError("La date de début ne peut pas être dans le passé.")
            
            if self.type_conge and self.type_conge.duree_max:
                duree = (self.date_fin - self.date_debut).days + 1
                if duree > self.type_conge.duree_max:
                    raise ValidationError(f"La durée maximale pour ce type de congé est de {self.type_conge.duree_max} jours.")
    
    def save(self, *args, **kwargs):
        if self.pk:
            old_conge = Conge.objects.get(pk=self.pk)
            if old_conge.statut != self.statut and self.statut in ['Approuvé', 'Rejeté']:
                self.date_traitement = timezone.now()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Congé de {self.employe} du {self.date_debut} au {self.date_fin}"
    
    class Meta:
        verbose_name = "Congé"
        verbose_name_plural = "Congés"
        ordering = ['-date_demande']