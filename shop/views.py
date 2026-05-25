import logging
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Pizza, PizzaCategory, PizzaSize, PizzaPrice, Order, OrderItem, Courier, PickupPoint
from users.models import UserProfile
from main.models import PromoCode

logger = logging.getLogger('shop')


def pizza_list_view(request):
    pizzas = Pizza.objects.filter(is_active=True).select_related('category', 'sauce')
    categories = PizzaCategory.objects.all()

    q = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sauce_id = request.GET.get('sauce', '')
    sort = request.GET.get('sort', 'name')

    if q:
        pizzas = pizzas.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(ingredients__icontains=q))
    if category_id:
        pizzas = pizzas.filter(category_id=category_id)
    if sauce_id:
        pizzas = pizzas.filter(sauce_id=sauce_id)
    if min_price:
        pizzas = pizzas.filter(pizza_prices__price__gte=min_price).distinct()
    if max_price:
        pizzas = pizzas.filter(pizza_prices__price__lte=max_price).distinct()

    sort_map = {
        'name': 'name',
        '-name': '-name',
        'price': 'pizza_prices__price',
        '-price': '-pizza_prices__price',
    }
    if sort in sort_map:
        pizzas = pizzas.order_by(sort_map[sort]).distinct()

    paginator = Paginator(pizzas, 12)
    page = paginator.get_page(request.GET.get('page', 1))

    from .models import Sauce
    sauces = Sauce.objects.all()

    return render(request, 'shop/pizza_list.html', {
        'page_obj': page,
        'categories': categories,
        'sauces': sauces,
        'q': q,
        'category_id': category_id,
        'sauce_id': sauce_id,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
    })


def pizza_detail_view(request, pk):
    pizza = get_object_or_404(Pizza, pk=pk, is_active=True)
    prices = pizza.pizza_prices.select_related('size').order_by('price')
    return render(request, 'shop/pizza_detail.html', {'pizza': pizza, 'prices': prices})


@login_required
def add_to_cart(request, pk):
    if request.method == 'POST':
        pizza = get_object_or_404(Pizza, pk=pk, is_active=True)
        size_id = request.POST.get('size_id')
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        key = f'{pk}_{size_id}'
        if key in cart:
            cart[key]['quantity'] += quantity
        else:
            try:
                pp = PizzaPrice.objects.get(pizza=pizza, size_id=size_id)
                cart[key] = {
                    'pizza_id': pk,
                    'pizza_name': pizza.name,
                    'size_id': size_id,
                    'size_name': pp.size.get_name_display(),
                    'unit_price': str(pp.price),
                    'quantity': quantity,
                }
            except PizzaPrice.DoesNotExist:
                messages.error(request, 'Выбранный размер недоступен.')
                return redirect('pizza_detail', pk=pk)
        request.session['cart'] = cart
        messages.success(request, f'{pizza.name} добавлена в корзину!')
        logger.info(f'User {request.user.username} added pizza {pizza.name} to cart')
    return redirect('cart')


@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    total = Decimal('0')
    for key, item in cart.items():
        subtotal = Decimal(item['unit_price']) * item['quantity']
        total += subtotal
        items.append({**item, 'key': key, 'subtotal': subtotal})
    return render(request, 'shop/cart.html', {'cart_items': items, 'total': total})


@login_required
def remove_from_cart(request, key):
    cart = request.session.get('cart', {})
    if key in cart:
        del cart[key]
        request.session['cart'] = cart
        messages.info(request, 'Товар удалён из корзины.')
    return redirect('cart')


@login_required
def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, 'Корзина пуста.')
        return redirect('pizza_list')

    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        messages.error(request, 'Заполните профиль перед оформлением заказа.')
        return redirect('users:profile')

    pickup_points = PickupPoint.objects.filter(is_active=True)

    if request.method == 'POST':
        delivery_type = request.POST.get('delivery_type', 'delivery')
        delivery_address = request.POST.get('delivery_address', '')
        pickup_id = request.POST.get('pickup_point', '')
        promo_code_str = request.POST.get('promo_code', '').strip()
        comment = request.POST.get('comment', '')

        discount = 0
        if promo_code_str:
            from django.utils import timezone
            today = timezone.now().date()
            try:
                promo = PromoCode.objects.get(
                    code__iexact=promo_code_str, status='active',
                    valid_from__lte=today, valid_to__gte=today
                )
                discount = promo.discount_percent
            except PromoCode.DoesNotExist:
                messages.warning(request, 'Промокод недействителен.')

        total = Decimal('0')
        for item in cart.values():
            total += Decimal(item['unit_price']) * item['quantity']
        if discount:
            total = total * (100 - discount) / 100

        pickup_point = None
        if delivery_type == 'pickup' and pickup_id:
            try:
                pickup_point = PickupPoint.objects.get(pk=pickup_id)
            except PickupPoint.DoesNotExist:
                pass

        order = Order.objects.create(
            client=profile,
            status='new',
            delivery_type=delivery_type,
            delivery_address=delivery_address if delivery_type == 'delivery' else '',
            pickup_point=pickup_point,
            promo_code=promo_code_str,
            discount_percent=discount,
            total_price=total,
            comment=comment,
        )

        for item in cart.values():
            OrderItem.objects.create(
                order=order,
                pizza_id=item['pizza_id'],
                size_id=item['size_id'],
                quantity=item['quantity'],
                unit_price=Decimal(item['unit_price']),
            )

        request.session['cart'] = {}
        logger.info(f'Order #{order.pk} created by {request.user.username}')
        messages.success(request, f'Заказ #{order.pk} оформлен!')
        return redirect('order_detail', pk=order.pk)

    items = []
    total = Decimal('0')
    for key, item in cart.items():
        subtotal = Decimal(item['unit_price']) * item['quantity']
        total += subtotal
        items.append({**item, 'key': key, 'subtotal': subtotal})

    return render(request, 'shop/checkout.html', {
        'cart_items': items,
        'total': total,
        'pickup_points': pickup_points,
    })


@login_required
def order_list_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return render(request, 'shop/order_list.html', {'orders': []})

    if request.user.is_superuser:
        orders = Order.objects.select_related('client', 'courier').all()
    elif profile.role == 'employee':
        orders = Order.objects.select_related('client', 'courier').filter(
            status__in=['new', 'preparing', 'delivering']
        )
    else:
        orders = Order.objects.filter(client=profile).select_related('courier')

    sort = request.GET.get('sort', '-created_at')
    q = request.GET.get('q', '')
    if q:
        orders = orders.filter(
            Q(client__user__username__icontains=q) |
            Q(pk__icontains=q)
        )
    sort_fields = ['-created_at', 'created_at', '-total_price', 'total_price', 'status']
    if sort in sort_fields:
        orders = orders.order_by(sort)

    return render(request, 'shop/order_list.html', {
        'orders': orders,
        'sort': sort,
        'q': q,
    })


@login_required
def order_detail_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = None

    if not request.user.is_superuser:
        if profile is None:
            return redirect('home')
        if profile.role not in ('employee',) and order.client != profile:
            return redirect('home')

    return render(request, 'shop/order_detail.html', {'order': order})


@login_required
def update_order_status(request, pk):
    if not request.user.is_superuser and not getattr(getattr(request.user, 'profile', None), 'role', '') == 'employee':
        return redirect('home')
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            logger.info(f'Order #{pk} status changed to {new_status} by {request.user.username}')
            messages.success(request, 'Статус заказа обновлён.')
    return redirect('order_detail', pk=pk)


def _make_bar_chart_b64(labels, values, title, xlabel='', ylabel='', color='#dc3545'):
    import io, base64
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 4))
    if labels and values:
        bars = ax.bar(labels, values, color=color, edgecolor='white', linewidth=0.5)
        ax.bar_label(bars, fmt='%.0f', padding=3, fontsize=8)
    ax.set_title(title, fontsize=13, pad=10)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis='x', rotation=30, labelsize=8)
    ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=110, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def _make_pie_chart_b64(labels, values, title):
    import io, base64
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 5))
    palette = ['#dc3545', '#fd7e14', '#ffc107', '#198754', '#0d6efd',
               '#6610f2', '#20c997', '#d63384', '#0dcaf0', '#adb5bd']
    if labels and values:
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, autopct='%1.0f%%',
            colors=palette[:len(labels)], startangle=140,
            textprops={'fontsize': 8}
        )
    ax.set_title(title, fontsize=12, pad=10)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=110, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def statistics_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('home')

    from django.db.models.functions import TruncMonth

    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(status='delivered').aggregate(
        total=Sum('total_price')
    )['total'] or 0

    orders_per_client = (
        Order.objects.values('client__user__username')
        .annotate(cnt=Count('id'))
        .order_by('-cnt')[:10]
    )

    revenue_per_courier = (
        Order.objects.filter(status='delivered', courier__isnull=False)
        .values('courier__profile__user__username')
        .annotate(total=Sum('total_price'))
        .order_by('-total')[:10]
    )

    popular_pizzas = (
        OrderItem.objects.values('pizza__name')
        .annotate(cnt=Count('id'))
        .order_by('-cnt')[:8]
    )

    monthly_revenue = (
        Order.objects.filter(status='delivered')
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('total_price'))
        .order_by('month')
    )

    orders_by_status = (
        Order.objects.values('status')
        .annotate(cnt=Count('id'))
        .order_by('-cnt')
    )

    avg_order = Order.objects.filter(status='delivered').aggregate(avg=Avg('total_price'))['avg'] or 0

    # Python-generated charts (matplotlib)
    monthly_labels = [r['month'].strftime('%m/%Y') for r in monthly_revenue if r['month']]
    monthly_values = [float(r['total']) for r in monthly_revenue]
    chart_revenue_b64 = _make_bar_chart_b64(
        monthly_labels, monthly_values,
        'Выручка по месяцам (доставленные заказы)', xlabel='Месяц', ylabel='Выручка, руб.'
    )

    pizza_labels = [r['pizza__name'] for r in popular_pizzas]
    pizza_values = [r['cnt'] for r in popular_pizzas]
    chart_pizzas_b64 = _make_pie_chart_b64(pizza_labels, pizza_values, 'Популярность пицц')

    status_labels = [dict(Order.STATUS_CHOICES).get(r['status'], r['status']) for r in orders_by_status]
    status_values = [r['cnt'] for r in orders_by_status]
    chart_status_b64 = _make_bar_chart_b64(
        status_labels, status_values,
        'Заказы по статусам', ylabel='Количество', color='#0d6efd'
    )

    return render(request, 'shop/statistics.html', {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'avg_order': round(avg_order, 2),
        'orders_per_client': orders_per_client,
        'revenue_per_courier': revenue_per_courier,
        'popular_pizzas': popular_pizzas,
        'chart_revenue_b64': chart_revenue_b64,
        'chart_pizzas_b64': chart_pizzas_b64,
        'chart_status_b64': chart_status_b64,
    })


def pickup_points_view(request):
    points = PickupPoint.objects.filter(is_active=True)
    return render(request, 'shop/pickup_points.html', {'points': points})


# CRUD for Pizza (admin-level)
@login_required
def pizza_create_view(request):
    if not request.user.is_superuser:
        return redirect('home')
    from .forms import PizzaForm
    if request.method == 'POST':
        form = PizzaForm(request.POST, request.FILES)
        if form.is_valid():
            pizza = form.save()
            logger.info(f'Pizza created: {pizza.name} by {request.user.username}')
            messages.success(request, 'Пицца добавлена.')
            return redirect('pizza_list')
    else:
        form = PizzaForm()
    return render(request, 'shop/pizza_form.html', {'form': form, 'action': 'Добавить'})


@login_required
def pizza_update_view(request, pk):
    if not request.user.is_superuser:
        return redirect('home')
    from .forms import PizzaForm
    pizza = get_object_or_404(Pizza, pk=pk)
    if request.method == 'POST':
        form = PizzaForm(request.POST, request.FILES, instance=pizza)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пицца обновлена.')
            return redirect('pizza_detail', pk=pk)
    else:
        form = PizzaForm(instance=pizza)
    return render(request, 'shop/pizza_form.html', {'form': form, 'action': 'Изменить', 'pizza': pizza})


@login_required
def pizza_delete_view(request, pk):
    if not request.user.is_superuser:
        return redirect('home')
    pizza = get_object_or_404(Pizza, pk=pk)
    if request.method == 'POST':
        pizza.delete()
        messages.success(request, 'Пицца удалена.')
        return redirect('pizza_list')
    return render(request, 'shop/pizza_confirm_delete.html', {'pizza': pizza})

