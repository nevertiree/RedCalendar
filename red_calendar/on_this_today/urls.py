# -*- coding: utf-8 -*-

from django.urls import path

from . import views

urlpatterns = [
    # example: /on_this_today/
    path('', views.index, name='index'),

    # example: /on_this_today/add_new_event
    path('add_new_event', views.add_new_event, name='add_new_event'),

    # example: /on_this_today/month/12/
    path('month/<int:_month>', views.month_query, name='month_query'),

    # example: /on_this_today/year/1991/
    path('year/<int:_year>', views.year_query, name='year_query'),
]
