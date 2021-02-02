from django.urls import path
from django.urls import re_path
from . import views

urlpatterns = [
    path('', views.home, name="articles-home"),
    path('about/', views.about, name="about"),
    path('mostrecent/', views.mostrecent, name="most-recent"),
    path('api/', views.mostrecentapi, name="most-recent-api"),
    path('search/', views.search, name="articles-search"),
    path('article/', views.article, name="article-profile"),
    path('journals/', views.journals, name="journal-list")


]
