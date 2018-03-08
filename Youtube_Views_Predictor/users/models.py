from django.db import models

# Create your models here.

class users(models.Model):
    Email = models.CharField(max_length = 100)
    Display_Name = models.CharField(max_length=50)
    Password=models.CharField(max_length = 100)