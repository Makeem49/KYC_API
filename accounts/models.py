from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class User(AbstractUser):

    CHOICE = [
        (True, 'True'),
        (False, 'False')
    ]

    username = models.CharField(max_length=100, unique=True, null=True)
    email = models.EmailField(_("email address"), unique=True, null=False)
    is_active = models.BooleanField(choices=CHOICE, default=True)
    position = models.CharField(max_length=20, null=False, blank=False)

    
    class Meta:
        ordering = ['-id']
    

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email}"

