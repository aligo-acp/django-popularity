from django.db import models
from django.utils.module_loading import import_string
from django_action_reservation.reservation import Reservation

from django_popularity.actions import CrawlAction
from django_popularity.conf import settings
from django_popularity.fields import MIDField


class PopularityBase(models.Model):
    mid = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    geo = models.CharField(max_length=255)
    score30 = models.FloatField(default=0)
    score90 = models.FloatField(default=0)
    score180 = models.FloatField(default=0)
    score360 = models.FloatField(default=0)
    score1080 = models.FloatField(default=0)

    class Meta:
        abstract = True

    def update_score(self):
        calculator = import_string(settings.POPULARITY_CALCULATOR)
        self.score1080 = calculator(1080).calculate(self)
        self.score360 = calculator(360).calculate(self)
        self.score180 = calculator(180).calculate(self)
        self.score90 = calculator(90).calculate(self)
        self.score30 = calculator(30).calculate(self)
        self.save()


class Popularity(PopularityBase):
    standard = models.OneToOneField('django_popularity.Standard', models.DO_NOTHING, related_name='popularity1')
    standard2 = models.OneToOneField('django_popularity.Standard', models.DO_NOTHING, related_name='popularity2')
    graph = models.OneToOneField('django_popularity.Graph', models.DO_NOTHING, related_name='popularity')

    objects = models.Manager()
    action_reservation = Reservation([CrawlAction])

    @staticmethod
    def init_all_geo(suggestion):
        obj = Popularity(
            mid=suggestion.mid,
            title=suggestion.title,
            type=suggestion.type,
        )
        for geo in GeoStandard.objects.values_list('geo', flat=True):
            obj.geo = geo
            obj.standard, obj.standard2 = Standard.creates_by_geo(geo)
            obj.graph = Graph.objects.create()
            obj.pk = None
            obj.save()
            obj.reserve_crawl()

    @staticmethod
    def init_geo_by_mid(mid, geo):
        obj = Popularity.objects.filter(mid=mid).first()
        obj.pk = None
        obj.graph = Graph.objects.create()
        obj.geo = geo
        obj.standard, obj.standard2 = Standard.creates_by_geo(geo)
        obj.save()
        obj.reserve_crawl()

    def reserve_crawl(self):
        self.reserve_action('crawl')


class Standard(PopularityBase):
    graph = models.OneToOneField('django_popularity.Graph', models.DO_NOTHING, related_name='standard')
    is_top = models.BooleanField()

    @staticmethod
    def creates_by_geo(geo):
        geo_std = GeoStandard.objects.get(geo=geo)
        top_std = Standard.objects.create(
            title=geo_std.top_title,
            type=geo_std.top_type,
            mid=geo_std.top_mid,
            geo=geo,
            is_top=True,
            graph=Graph.objects.create(),
        )
        bot_std = Standard.objects.create(
            title=geo_std.bot_title,
            type=geo_std.bot_type,
            mid=geo_std.bot_mid,
            geo=geo,
            is_top=False,
            graph=Graph.objects.create(),
        )
        return [bot_std, top_std]


class Graph(models.Model):
    pass


class DateGraphPoint(models.Model):
    graph = models.ForeignKey('django_popularity.Graph', models.CASCADE, 'date_points')
    date = models.DateField()
    value = models.PositiveIntegerField()

    class Meta:
        ordering = ['date']


class GeoStandard(models.Model):
    geo = models.CharField(
        max_length=100,
        unique=True,
        choices=(
            ('US', 'US'),
            ('JP', 'JP'),
            ('GB', 'GB'),
            ('FR', 'FR'),
            ('DE', 'DE'),
            ('TH', 'TH'),
            ('SG', 'SG'),
            ('IT', 'IT'),
            ('KR', 'KR'),
        )
    )
    top_mid = MIDField(max_length=100)
    top_title = models.CharField(max_length=100)
    top_type = models.CharField(max_length=100)
    bot_mid = MIDField(max_length=100)
    bot_title = models.CharField(max_length=100)
    bot_type = models.CharField(max_length=100)


class SuggestionResult(models.Model):
    type = models.CharField(max_length=100)
    mid = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=100)

    @staticmethod
    def creates_from_search_result(result):
        for row in result:
            SuggestionResult.objects.update_or_create(
                {'mid': row['mid']}, title=row['title'], type=row['type']
            )
