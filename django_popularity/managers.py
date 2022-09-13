from datetime import timedelta

from django.db.models import (Avg, CharField, IntegerField, Manager, OuterRef,
                              Q, QuerySet, Subquery, Value)
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


class PopularityQuerySet(QuerySet):
    def reserve_update(self):
        self.model.reserve
        for obj in self:
            obj.reserve_update()


class PopularityManager(Manager.from_queryset(PopularityQuerySet)):
    def get_queryset(self, base_days=settings.POPULARITY_DEFAULT_BASE_DAYS):
        score = Avg(
            'graph__date_points__value',
            filter=Q(graph__date_points__date__gte=now() - timedelta(days=base_days))
        )
        qs = super().get_queryset()
        return  qs\
                    .annotate(base_days=Value(base_days, IntegerField())) \
                    .annotate(score=score)

    