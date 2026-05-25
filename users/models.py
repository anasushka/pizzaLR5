import re
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


PHONE_REGEX = r'^\+375 \((?:29|33|25|44)\) \d{3}-\d{2}-\d{2}$'


def validate_phone(value):
    if not re.match(PHONE_REGEX, value):
        raise ValidationError('Номер телефона должен быть в формате: +375 (29) XXX-XX-XX')


def validate_age_18(value):
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError('Возраст должен быть не менее 18 лет.')


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('buyer', 'Покупатель'),
        ('employee', 'Сотрудник'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='buyer')
    birth_date = models.DateField(validators=[validate_age_18])
    phone = models.CharField(max_length=20, validators=[validate_phone])
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} ({self.get_role_display()})'

    @property
    def age(self):
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
