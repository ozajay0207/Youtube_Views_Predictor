from django.db import models

# Create your models here.
class contact_us_form(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length = 100)
    message=models.CharField(max_length =1000)
    def __str__(self):
        return self.first_name
