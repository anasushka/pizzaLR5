from django.urls import path
from . import views

urlpatterns = [
    path('weather/', views.weather_api, name='api_weather'),
    path('currency/', views.currency_api, name='api_currency'),
    path('pizzas/', views.pizzas_api, name='api_pizzas'),
    path('orders/', views.orders_api, name='api_orders'),
    path('stats/', views.stats_api, name='api_stats'),
]
