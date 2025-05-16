from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    
    # Champs supplémentaires si nécessaire
    is_employee = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def save(self, *args, **kwargs):
        # Créer l'utilisateur
        super().save(*args, **kwargs)
        
        # Assigner au groupe approprié si c'est un nouvel utilisateur
        if self.is_employee and not self.groups.filter(name='Employés').exists():
            employees_group, _ = Group.objects.get_or_create(name='Employés')
            self.groups.add(employees_group)
        
        if self.is_admin and not self.groups.filter(name='Administrateurs').exists():
            admins_group, _ = Group.objects.get_or_create(name='Administrateurs')
            self.groups.add(admins_group)