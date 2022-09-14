import importlib

from django import forms
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_action_reservation.admin import (ActionReservationAdmin,
                                             create_reservation_inline)

from django_popularity.conf import settings
from django_popularity.models import (GeoStandard, Popularity, Standard,
                                      SuggestionResult)


class GeoFilter(SimpleListFilter):
    title = 'geo'
    parameter_name = 'geo'

    def lookups(self, request, model_admin):
        return [
            (geo.geo, geo.geo)
            for geo in GeoStandard.objects.all()
        ]

    def choices(self, changelist):
        choices = list(super().choices(changelist))
        choices[0]['display'] = 'default(%s)' % settings.POPULARITY_DEFAULT_GEO
        return choices

    def queryset(self, request, queryset):
        return queryset


def create_proxy_model(model, name):
    class Meta:
        proxy = True

    proxy_model = type(
        name,
        (model, ),
        {
            'Meta': Meta,
            '__module__': model.__module__,
        }
    )
    module = importlib.import_module(model.__module__)
    setattr(module, name, proxy_model)
    return proxy_model


def register_proxy_model(model, name, site=None):
    return admin.register(
        create_proxy_model(model, name),
        site=site
    )


class RegisterMIDAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'mid_checked_by_admin',
        'mid',
    )
    list_display_extra = tuple()
    ordering = (
        'mid_checked_by_admin',
        'id',
    )
    list_filter = (
        'mid_checked_by_admin',
    )

    def title(self, obj):
        return obj.title

    def get_list_display(self, request):
        return self.list_display_extra + super().get_list_display(request)

    def get_queryset(self, request):
        return self.model.objects_with_mid_info()

    def save_model(self, request, obj, form, change):
        obj.mid_checked_by_admin = True
        if obj.mid:
            suggestion = SuggestionResult.objects.get(mid=obj.mid)
            if not Popularity.objects.filter(mid=obj.mid).exists():
                Popularity.init_all_geo(suggestion)
        obj.save()


@admin.action(description='calculate scores')
def calculate_scores(modeladmin, request, queryset):
    for obj in queryset:
        obj.update_score()


@admin.action(description='reserve crawl')
def reserve_crawl(modeladmin, request, queryset):
    queryset.reserve('crawl')


@admin.register(Popularity)
class PopularitAdmin(admin.ModelAdmin):
    fields = (
        'mid',
        'title',
        'type',
        'geo',
        'visualization',
    )
    readonly_fields = (
        'mid',
        'title',
        'type',
        'geo',
        'visualization',
    )
    list_display = (
        'title',
        'updated',
        'geo',
        'updated',
        'score1080',
        'score360',
        'score180',
        'score90',
    )
    list_filter = (
        'geo',
    )
    inlines = (
        create_reservation_inline(Popularity, extra=1),
    )
    actions = [calculate_scores, reserve_crawl]

    def get_queryset(self, request):
        return self.model.objects_for_reserve.all()

    @property
    def media(self):
        media = super().media
        return media + forms.Media(js=['django_popularity/js/create_graph.js'])

    def visualization(self, obj):
        request_url = reverse('popularity:visualization', kwargs={'pk': obj.pk})
        return mark_safe(
            f'<canvas data-request_url="{request_url}" height="200" id="visualization"></canvas>'
        )


@admin.register(GeoStandard)
class GeoStandardAdmin(admin.ModelAdmin):
    fields = (
        'geo',
        'top_title',
        'top_mid',
        'bot_title',
        'bot_mid',
    )
    list_display = (
        'geo',
        'top_title',
        'bot_title',
    )

    def get_readonly_fields(self, request, obj=None):
        ret = (
            'top_title',
            'bot_title',
        )
        return ret + ('geo', ) if obj else ret

    def save_model(self, request, obj, form, change):
        suggestion = SuggestionResult.objects.get(mid=obj.top_mid)
        obj.top_type = suggestion.type
        obj.top_title = suggestion.title

        suggestion = SuggestionResult.objects.get(mid=obj.bot_mid)
        obj.bot_type = suggestion.type
        obj.bot_title = suggestion.title

        if not obj.pk:
            obj.save()
            for mid in Popularity.objects.values_list('mid', flat=True):
                Popularity.init_geo_by_mid(mid, obj.geo)
        else:
            prev_obj = GeoStandard.objects.get(id=obj.id)
            if prev_obj.top_mid != obj.top_mid or prev_obj.bot_mid != obj.bot_mid:
                Standard.objects.filter(geo=prev_obj.geo, is_top=True).update(
                    title=obj.top_title, mid=obj.top_mid, type=obj.top_type
                )
                Standard.objects.filter(geo=prev_obj.geo, is_top=False).update(
                    title=obj.bot_title, mid=obj.bot_mid, type=obj.bot_type
                )
                Popularity.objects_for_reserve.filter(geo=obj.geo).reserve('crawl')
            obj.save()


admin.site.register(Popularity.reservation_model, ActionReservationAdmin)
