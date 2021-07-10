# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from app import views
from app.views import *
from campaign.views import *

urlpatterns = [
    # Matches any html file 
    re_path(r'^.*\.html', views.pages, name='pages'),

    # The home page
    path('', views.index, name='home'),
    path('campaign/',campaign, name='campaign'),
    path('donation/', views.donation, name='donation'),
    path('update_profile/<str:pk>/', views.updateProfile, name="update_profile"),
    path('salaTime/<str:pk>/', views.salaTime, name="salaTime"),
    

]
