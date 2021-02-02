#from djongo import models
from django.db import models


class Author(models.Model):
    name = models.TextField()

# Create your models here.
class Article(models.Model):
    title = models.TextField()
    abstract = models.TextField()
    #Array model field from Djongo
    #authors = models.ArrayModelField(model_container=Author)
    publisher = models.TextField()
    journal = models.TextField()
    #issn = models.TextField()
    datepublished = models.DateField()
    source_link = models.URLField()
    isopenaccess = models.BooleanField()
