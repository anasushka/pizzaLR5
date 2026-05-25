from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('news/', views.news_list_view, name='news'),
    re_path(r'^news/(?P<pk>\d+)/$', views.article_detail_view, name='article_detail'),
    path('glossary/', views.glossary_view, name='glossary'),
    path('contacts/', views.contacts_view, name='contacts'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('vacancies/', views.vacancies_view, name='vacancies'),
    path('reviews/', views.reviews_view, name='reviews'),
    path('promo/', views.promo_view, name='promo'),
]
