from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.BasePageView.as_view(), name='base'),
    url(r'^pickban/', views.PickBanView.as_view(), name='pick_ban'),
]
