from django.db import models
from django.core.validators import MinValueValidator
from users.models import UserProfile


class Sauce(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        verbose_name = 'Соус'
        verbose_name_plural = 'Соусы'

    def __str__(self):
        return self.name


class PizzaCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Категория пиццы'
        verbose_name_plural = 'Категории пиццы'

    def __str__(self):
        return self.name


class PizzaSize(models.Model):
    SIZE_CHOICES = [
        ('small', 'Маленькая (25 см)'),
        ('medium', 'Средняя (30 см)'),
        ('large', 'Большая (35 см)'),
        ('xlarge', 'Семейная (40 см)'),
    ]
    name = models.CharField(max_length=10, choices=SIZE_CHOICES, unique=True, verbose_name='Размер')
    diameter_cm = models.PositiveSmallIntegerField(verbose_name='Диаметр (см)')

    class Meta:
        verbose_name = 'Размер пиццы'
        verbose_name_plural = 'Размеры пиццы'

    def __str__(self):
        return self.get_name_display()


class Pizza(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='pizzas/', blank=True, null=True, verbose_name='Фото')
    category = models.ForeignKey(
        PizzaCategory, on_delete=models.SET_NULL, null=True,
        related_name='pizzas', verbose_name='Категория'
    )
    sauce = models.ForeignKey(
        Sauce, on_delete=models.SET_NULL, null=True,
        related_name='pizzas', verbose_name='Соус'
    )
    # ManyToMany with PizzaSize via PizzaPrice
    sizes = models.ManyToManyField(PizzaSize, through='PizzaPrice', verbose_name='Размеры')
    ingredients = models.TextField(verbose_name='Состав', blank=True)
    weight_g = models.PositiveIntegerField(default=500, verbose_name='Вес (г)')
    calories = models.PositiveIntegerField(default=0, verbose_name='Калории')
    is_active = models.BooleanField(default=True, verbose_name='В продаже')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Пицца'
        verbose_name_plural = 'Пиццы'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_min_price(self):
        prices = self.pizza_prices.order_by('price')
        return prices.first().price if prices.exists() else 0


class PizzaPrice(models.Model):
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE, related_name='pizza_prices')
    size = models.ForeignKey(PizzaSize, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Цена пиццы'
        verbose_name_plural = 'Цены пиццы'
        unique_together = ('pizza', 'size')

    def __str__(self):
        return f'{self.pizza.name} ({self.size}) — {self.price} руб.'


class Ingredient(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    price_extra = models.DecimalField(
        max_digits=6, decimal_places=2, default=0,
        verbose_name='Доп. цена'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class PickupPoint(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    address = models.CharField(max_length=300, verbose_name='Адрес')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    working_hours = models.CharField(max_length=100, default='09:00-22:00', verbose_name='Часы работы')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        verbose_name = 'Точка самовывоза'
        verbose_name_plural = 'Точки самовывоза'

    def __str__(self):
        return self.name


class Courier(models.Model):
    # OneToOne relation: Courier profile linked to UserProfile
    profile = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE,
        related_name='courier_profile', verbose_name='Профиль'
    )
    vehicle = models.CharField(max_length=100, blank=True, verbose_name='Транспорт')
    is_available = models.BooleanField(default=True, verbose_name='Доступен')
    hired_at = models.DateField(auto_now_add=True, verbose_name='Дата найма')

    class Meta:
        verbose_name = 'Курьер'
        verbose_name_plural = 'Курьеры'

    def __str__(self):
        return str(self.profile)

    def total_earnings(self):
        from django.db.models import Sum
        result = self.orders.filter(status='delivered').aggregate(
            total=Sum('total_price')
        )
        return result['total'] or 0


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('preparing', 'Готовится'),
        ('delivering', 'Доставляется'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]
    DELIVERY_CHOICES = [
        ('delivery', 'Доставка'),
        ('pickup', 'Самовывоз'),
    ]

    client = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE,
        related_name='orders', verbose_name='Клиент'
    )
    courier = models.ForeignKey(
        Courier, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='orders', verbose_name='Курьер'
    )
    pickup_point = models.ForeignKey(
        PickupPoint, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='orders', verbose_name='Точка самовывоза'
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_CHOICES, default='delivery', verbose_name='Тип доставки')
    delivery_address = models.CharField(max_length=300, blank=True, verbose_name='Адрес доставки')
    promo_code = models.CharField(max_length=50, blank=True, verbose_name='Промокод')
    discount_percent = models.PositiveSmallIntegerField(default=0, verbose_name='Скидка %')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Итого')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    delivery_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата доставки')
    comment = models.TextField(blank=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.pk} — {self.client} ({self.get_status_display()})'

    def calculate_total(self):
        total = sum(item.get_subtotal() for item in self.items.all())
        if self.discount_percent:
            total = total * (100 - self.discount_percent) / 100
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE, verbose_name='Пицца')
    size = models.ForeignKey(PizzaSize, on_delete=models.CASCADE, verbose_name='Размер')
    quantity = models.PositiveSmallIntegerField(default=1, verbose_name='Количество')
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена за шт.')

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.pizza.name} x{self.quantity}'

    def get_subtotal(self):
        from decimal import Decimal
        return Decimal(str(self.unit_price)) * self.quantity

