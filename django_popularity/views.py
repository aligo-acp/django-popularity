from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView

from django_popularity import serializers
from django_popularity.conf import settings
from django_popularity.models import Popularity, SuggestionResult


def search_mid_popup_view(request):
    context = {
        'keyword': request.GET.get('keyword', ''),
        'target_id': request.GET.get('target_id')
    }
    if context['keyword']:
        context['results'] = settings.POPULARITY_PYTRENDS.suggestions(context['keyword'])
        if context['results']:
            SuggestionResult.creates_from_search_result(context['results'])
    return render(
        request,
        'django_popularity/search_mid_popup.html',
        context
    )


class PopularityVisualizationAPIView(RetrieveAPIView):
    serializer_class = serializers.PopularitySerializer
    queryset = Popularity.objects.all()
