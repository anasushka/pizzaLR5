from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.pizza_list_view, name='pizza_list'),
    re_path(r'^pizza/(?P<pk>\d+)/$', views.pizza_detail_view, name='pizza_detail'),
    re_path(r'^pizza/(?P<pk>\d+)/add-to-cart/$', views.add_to_cart, name='add_to_cart'),
    path('pizza/create/', views.pizza_create_view, name='pizza_create'),
    re_path(r'^pizza/(?P<pk>\d+)/edit/$', views.pizza_update_view, name='pizza_update'),
    re_path(r'^pizza/(?P<pk>\d+)/delete/$', views.pizza_delete_view, name='pizza_delete'),
    path('cart/', views.cart_view, name='cart'),
    re_path(r'^cart/remove/(?P<key>[\w_]+)/$', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.order_list_view, name='order_list'),
    re_path(r'^orders/(?P<pk>\d+)/$', views.order_detail_view, name='order_detail'),
    re_path(r'^orders/(?P<pk>\d+)/status/$', views.update_order_status, name='update_order_status'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('pickup-points/', views.pickup_points_view, name='pickup_points'),
    path('parallel/', views.parallel_demo_view, name='parallel_demo'),
    path('parallel/run/', views.run_parallel_demo, name='run_parallel_demo'),
]
