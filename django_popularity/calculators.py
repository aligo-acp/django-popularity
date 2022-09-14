from datetime import timedelta

from django.db.models import Avg, F, Q
from django.utils.timezone import now


class BaseCalculator:
    def __init__(self, base_days):
        self.base_days = base_days

    def annotate_score(self, queryset, name):
        score = Avg(
            'graph__date_points__value',
            filter=Q(graph__date_points__date__gte=now() - timedelta(days=self.base_days))
        )
        return queryset.annotate(**{name: score})


class DefaultCalculator(BaseCalculator):
    def annotate_score(self, queryset, name):
        qs = super().annotate_score(queryset, 'self_score')
        qs = self.annotate_std_score(qs, 'std_score')
        qs = self.annotate_std2_score(qs, 'std2_score')
        score = (
            F('self_score') /
            (F('std_score') + F('std2_score') + F('self_score'))
            * 100
        )
        return qs.annotate(**{name: score})
    
    def annotate_std_score(self, queryset, name):
        std_score = Avg(
            'standard__graph__date_points__value',
            filter=Q(standard__graph__date_points__date__gte=now() - timedelta(days=self.base_days))
        )
        return queryset.annotate(**{name: std_score})

    def annotate_std2_score(self, queryset, name):
        std2_score = Avg(
            'standard2__graph__date_points__value',
            filter=Q(standard2__graph__date_points__date__gte=now() - timedelta(days=self.base_days))
        )
        return queryset.annotate(**{name: std2_score})
