from django.urls import path

from django_popularity import views

app_name = 'popularity'

urlpatterns = [
    path('search-mid-popup/', views.search_mid_popup_view, name='search_mid_popup'),
    path('visualization/<int:pk>/', views.PopularityVisualizationAPIView.as_view(), name='visualization'),
]
