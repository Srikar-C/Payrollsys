from django.db import models
from django.contrib.auth.models import User
class Registration(models.Model):
    username=models.CharField(max_length=255)
    password=models.CharField(max_length=255)
    Email=models.EmailField()
    UserType=models.CharField(100, choices=(
            ('employee','Employee'),
            ('employer','Employer'),
            ('admin','Admin')
    ),max_length=255)
