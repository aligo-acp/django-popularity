from datetime import datetime, timedelta

from django.db.models import Avg


class BaseCalculator:
    def __init__(self, base_days):
        self.base_days = base_days
        self.today = datetime.today()

    def calculate(self, obj):
        return self.avg(obj.graph)

    def avg(self, graph):
        return graph.date_points \
                    .filter(date__gte=self.today-timedelta(days=self.base_days)) \
                    .aggregate(Avg('value'))['value__avg'] or 0


class DefaultCalculator(BaseCalculator):
    def calculate(self, obj):
        avg_self = self.avg(obj.graph)
        avg_std1 = self.avg(obj.standard.graph)
        avg_std2 = self.avg(obj.standard2.graph)
        avg_total = avg_self + avg_std1 + avg_std2
        denominator = avg_total or 1
        return (avg_self / denominator) * 100
