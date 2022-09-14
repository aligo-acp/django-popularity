from datetime import timedelta

from django.utils.timezone import now
from django_action_reservation.action import Action
from pytrends.request import TrendReq

from django_popularity.conf import settings

pytrends = TrendReq(
    hl='ko-KR', retries=5, backoff_factor=1, timeout=10,
    proxies=settings.POPULARITY_PROXIES,
)


class CrawlAction(Action):
    name = 'crawl'
    cool_time = settings.POPULARITY_CRAWL_COOL_TIME
    check_interval = settings.POPULARITY_RESERVATION_CHECK_INTERVAL

    def execute(self, obj):
        crawl_data = self.crawl(obj)
        self.update(obj, crawl_data)
        self.reserve(obj, now() + settings.POPULARITY_CRAWL_INTERVAL)

    def crawl(self, obj):
        self.build_payload(obj)
        row_dicts = []
        for row in pytrends.interest_over_time().iterrows():
            date = row[0]
            row_dict = dict(row[1])
            if row_dict['isPartial']:
                continue
            row_dict['date'] = date
            row_dicts.append(row_dict)
        return row_dicts

    def update(self, obj, data):
        self.update_graph(
            obj.graph,
            [{'date': r['date'], 'value': r[obj.mid]} for r in data]
        )
        self.update_graph(
            obj.standard.graph,
            [{'date': r['date'], 'value': r[obj.standard.mid]} for r in data]
        )
        self.update_graph(
            obj.standard2.graph,
            [{'date': r['date'], 'value': r[obj.standard2.mid]} for r in data]
        )
        obj.update_score()

    def update_graph(self, graph, data: list):
        from django_popularity.models import DateGraphPoint

        graph.date_points.all().delete()
        points = []
        for row in data:
            point = DateGraphPoint(graph=graph, date=row['date'], value=row['value'])
            points.append(point)
        DateGraphPoint.objects.bulk_create(points)


    def build_payload(self, obj):
        kw_list = [obj.mid, obj.standard.mid, obj.standard2.mid]
        end = now().strftime('%Y-%m-%d')
        start = (now() - timedelta(days=1080)).strftime('%Y-%m-%d')
        timeframe = '%s %s' % (start, end)

        pytrends.build_payload(kw_list, cat=0, timeframe=timeframe, geo=obj.geo, gprop='')


