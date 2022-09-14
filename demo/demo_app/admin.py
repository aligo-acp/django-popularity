from django.contrib import admin
from django_popularity.admin import (GeoFilter, RegisterMIDAdmin,
                                     register_proxy_model)

from . import models


@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):
    fields = (
        'name',
    )
    list_display = (
        'name',
        'geo',
        'popularity1080',
    )
    list_filter = (
        GeoFilter,
    )

    def geo(self, obj):
        return obj.geo

    def popularity1080(self, obj):
        return obj.score1080

    def get_list_display(self, request):
        return super().get_list_display(request)

    def get_queryset(self, request):
        kwargs = {}
        if geo := request.GET.get('geo'):
            kwargs['geo'] = geo
        return self.model.objects_with_popularity(**kwargs)


@register_proxy_model(models.Person, 'RegisterPersonMID')
class RegisterPersonMIDAdmin(RegisterMIDAdmin):
    list_display_extra = (
        'name',
    )

