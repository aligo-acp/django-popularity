import importlib

from django.db import models

from django_popularity.fields import MIDField
from django_popularity.managers import (objects_with_mid_info,
                                        objects_with_popularity)


class Popularity:
    def contribute_to_class(self, cls, name):
        MIDField(max_length=100, blank=True, unique=True).contribute_to_class(cls, 'mid')
        models.BooleanField(default=False).contribute_to_class(cls, 'mid_checked_by_admin')
        setattr(cls, 'objects_with_popularity', objects_with_popularity)
        setattr(cls, 'objects_with_mid_info', objects_with_mid_info)

        module = importlib.import_module(cls.__module__)
        proxy_model = self.create_proxy_model(cls)
        setattr(module, proxy_model.__name__, proxy_model)

    def create_proxy_model(self, cls):
        from django_popularity.models import (ProxyPopularity,
                                              ProxyPopularityMeta)

        name = cls.__name__ + 'Popularity'
        bases = (ProxyPopularity, )
        attrs = {
            'mid': models.ForeignKey(
                'demo_app.Person',
                models.CASCADE,
                to_field='mid',
                related_name='popularities',
                db_column='mid'
            ),
            'Meta': ProxyPopularityMeta,
            '__module__': cls.__module__,
        }
        return type(name, bases, attrs)
