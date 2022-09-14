from datetime import timedelta

from appconf import AppConf
from django.conf import settings
from pytrends.request import TrendReq


class DjangoPopularityAppConf(AppConf):
    DEFAULT_BASE_DAYS = 1080
    DEFAULT_GEO = 'KR'
    PYTRENDS = TrendReq(hl='en-EU')
    PROXIES = []
    CRAWL_COOL_TIME = 0
    CRAWL_INTERVAL = timedelta(days=1)
    RESERVATION_CHECK_INTERVAL = 10

    class Meta:
        prefix = 'popularity'
