from django.db import models
from django_popularity.popularity import Popularity


class Person(models.Model):
    name = models.CharField(max_length=100)

    popularity = Popularity()
