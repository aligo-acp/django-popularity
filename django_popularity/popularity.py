from django.db import models

from django_popularity.fields import MIDField
from django_popularity.managers import (objects_with_mid_info,
                                        objects_with_popularity)


class Popularity:
    def contribute_to_class(self, cls, name):
        MIDField(max_length=100, blank=True).contribute_to_class(cls, 'mid')
        models.BooleanField(default=False).contribute_to_class(cls, 'mid_checked_by_admin')
        setattr(cls, 'objects_with_popularity', objects_with_popularity)
        setattr(cls, 'objects_with_mid_info', objects_with_mid_info)
