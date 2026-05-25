"""
External APIs used:
  1. wttr.in — free weather API (no key required)
  2. Frankfurter API — free currency exchange rates (no key required)
"""
import logging
import requests
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from shop.models import Pizza, Order, PizzaCategory
from django.db.models import Count, Sum

logger = logging.getLogger('shop')


@api_view(['GET'])
@permission_classes([AllowAny])
def weather_api(request):
    city = request.GET.get('city', 'Minsk')
    try:
        url = f'https://wttr.in/{city}?format=j1'
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            current = data['current_condition'][0]
            return Response({
                'city': city,
                'temp_c': current['temp_C'],
                'feels_like': current['FeelsLikeC'],
                'description': current['weatherDesc'][0]['value'],
                'humidity': current['humidity'],
            })
        return Response({'error': 'Weather service unavailable'}, status=503)
    except Exception as e:
        logger.error(f'Weather API error: {e}')
        return Response({'error': str(e)}, status=503)


@api_view(['GET'])
@permission_classes([AllowAny])
def currency_api(request):
    base = request.GET.get('base', 'BYN')
    try:
        url = f'https://api.frankfurter.app/latest?from={base}&to=USD,EUR,RUB'
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return Response({
                'base': data.get('base', base),
                'date': data.get('date'),
                'rates': data.get('rates', {}),
            })
        return Response({'error': 'Currency service unavailable'}, status=503)
    except Exception as e:
        logger.error(f'Currency API error: {e}')
        return Response({'error': str(e)}, status=503)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pizzas_api(request):
    pizzas = Pizza.objects.filter(is_active=True).values(
        'id', 'name', 'description', 'category__name', 'sauce__name'
    )
    return Response(list(pizzas))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def orders_api(request):
    if not request.user.is_superuser:
        return Response({'error': 'Forbidden'}, status=403)
    orders = Order.objects.values('id', 'status', 'total_price', 'created_at').order_by('-created_at')[:50]
    return Response(list(orders))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_api(request):
    if not request.user.is_superuser:
        return Response({'error': 'Forbidden'}, status=403)
    data = {
        'total_orders': Order.objects.count(),
        'total_revenue': float(Order.objects.filter(status='delivered').aggregate(
            t=Sum('total_price')
        )['t'] or 0),
        'popular_pizza': list(
            Order.objects.values('items__pizza__name')
            .annotate(cnt=Count('items__pizza'))
            .order_by('-cnt')[:1]
        ),
        'timestamp': timezone.now().isoformat(),
    }
    return Response(data)

