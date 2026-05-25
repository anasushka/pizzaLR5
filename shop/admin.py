from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Sauce, PizzaCategory, Pizza, PizzaSize, PizzaPrice,
    Ingredient, PickupPoint, Courier, Order, OrderItem
)


@admin.register(Sauce)
class SauceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(PizzaCategory)
class PizzaCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(PizzaSize)
class PizzaSizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'diameter_cm')


class PizzaPriceInline(admin.TabularInline):
    model = PizzaPrice
    extra = 1
    fields = ('size', 'price')


@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'sauce', 'get_min_price', 'is_active', 'image_tag')
    list_filter = ('is_active', 'category', 'sauce')
    search_fields = ('name', 'description', 'ingredients')
    list_editable = ('is_active',)
    inlines = [PizzaPriceInline]
    fieldsets = (
        ('Основное', {'fields': ('name', 'description', 'image', 'category', 'sauce')}),
        ('Детали', {'fields': ('ingredients', 'weight_g', 'calories', 'is_active')}),
    )

    def get_min_price(self, obj):
        return obj.get_min_price()
    get_min_price.short_description = 'Мин. цена'

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="40"/>', obj.image.url)
        return '-'
    image_tag.short_description = 'Фото'


@admin.register(PizzaPrice)
class PizzaPriceAdmin(admin.ModelAdmin):
    list_display = ('pizza', 'size', 'price')
    list_filter = ('size',)
    search_fields = ('pizza__name',)


@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'working_hours', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name', 'address')


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ('profile', 'vehicle', 'is_available', 'hired_at', 'total_earnings')
    list_filter = ('is_available',)
    search_fields = ('profile__user__username', 'vehicle')

    def total_earnings(self, obj):
        return f'{obj.total_earnings()} руб.'
    total_earnings.short_description = 'Итого заработано'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('get_subtotal',)
    fields = ('pizza', 'size', 'quantity', 'unit_price', 'get_subtotal')

    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'Сумма'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'client', 'courier', 'status', 'delivery_type', 'total_price', 'created_at')
    list_filter = ('status', 'delivery_type')
    search_fields = ('client__user__username', 'delivery_address', 'pk')
    list_editable = ('status',)
    inlines = [OrderItemInline]
    readonly_fields = ('total_price', 'created_at')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Клиент', {'fields': ('client', 'courier')}),
        ('Доставка', {'fields': ('delivery_type', 'delivery_address', 'pickup_point')}),
        ('Скидка', {'fields': ('promo_code', 'discount_percent')}),
        ('Статус', {'fields': ('status', 'total_price', 'created_at', 'delivery_date', 'comment')}),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'pizza', 'size', 'quantity', 'unit_price')
    search_fields = ('pizza__name', 'order__pk')

