from django.urls import path

from . import views

urlpatterns = [
    path('', views.BasePageView.as_view(), name='base'),
    path('search/', views.SearchResultsView.as_view(), name='search_results'),
]
