from django.db import models
from django.utils import timezone
# Create your models here.

class Camers(models.Model):
    location = models.CharField(max_length=126)
    ip = models.CharField(max_length=20)
    port = models.CharField(max_length=10,blank = True)
    login = models.CharField(max_length=26, blank=True)
    password = models.CharField(max_length=126, blank=True)
    time_of_creation = models.DateTimeField(auto_now_add=True)


class EntryPersonLog(models.Model):
    date = models.CharField(max_length= 32)
    location = models.CharField(max_length=126)
    name = models.CharField(max_length=126)


class EntryCarLog(models.Model):
    date = models.CharField(max_length= 32)
    location = models.CharField(max_length=126)
    number = models.CharField(max_length= 32)

