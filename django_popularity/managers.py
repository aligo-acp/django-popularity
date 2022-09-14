from django.db.models import (CharField, IntegerField, Manager, OuterRef,
                              Subquery, Value)
from django.utils.module_loading import import_string
from django.utils.timezone import now

from django_popularity.conf import settings


@classmethod
def objects_with_popularity(
    cls,
    geo=settings.POPULARITY_DEFAULT_GEO,
    base_days=settings.POPULARITY_DEFAULT_BASE_DAYS
):
    from django_popularity.models import Popularity

    pops = Popularity.objects.get_queryset(base_days).filter(mid=OuterRef('mid'), geo=geo)
    return cls.objects \
               .annotate(geo=Value(geo, CharField(max_length=10))) \
               .annotate(base_days=Value(base_days, IntegerField())) \
               .annotate(popularity=Subquery(pops.values('score')[:1])) \
               .annotate(title=Subquery(pops.values('title')[:1]))


@classmethod
def objects_with_mid_info(cls):
    from django_popularity.models import SuggestionResult

    sugs = SuggestionResult.objects.filter(mid=OuterRef('mid'))
    return cls.objects \
              .annotate(type=Subquery(sugs.values('type'))) \
              .annotate(title=Subquery(sugs.values('title')))


class PopularityManager(Manager):
    def get_queryset(self, base_days=settings.POPULARITY_DEFAULT_BASE_DAYS):
        qs = super().get_queryset()
        qs = qs.annotate(base_days=Value(base_days, IntegerField()))
        calculator_cls = import_string(settings.POPULARITY_CALCULATOR)
        calculator = calculator_cls(base_days)
        return calculator.annotate_score(qs, 'score')

    