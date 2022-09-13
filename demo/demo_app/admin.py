from django.contrib import admin
from django_popularity.admin import (BaseDaysFilter, GeoFilter,
                                     RegisterMIDAdmin, register_proxy_model)

from . import models


@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):
    fields = (
        'name',
    )
    list_display = (
        'name',
        'geo',
        'popularity',
    )
    list_filter = (
        GeoFilter,
        BaseDaysFilter,
    )

    def geo(self, obj):
        return obj.geo

    def popularity(self, obj):
        return obj.popularity

    def get_list_display(self, request):
        return super().get_list_display(request)

    def get_queryset(self, request):
        kwargs = {}
        if geo := request.GET.get('geo'):
            kwargs['geo'] = geo
        if base_days := request.GET.get('base_days'):
            kwargs['base_days'] = int(base_days)
        return self.model.objects_with_popularity(**kwargs)


@register_proxy_model(models.Person, 'RegisterPersonMID')
class RegisterPersonMIDAdmin(RegisterMIDAdmin):
    list_display_extra = (
        'name',
    )

