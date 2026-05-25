from django.db import models
from django.contrib.auth.models import User


class CompanyInfo(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    logo = models.ImageField(upload_to='company/', blank=True, null=True, verbose_name='Логотип')
    founded_year = models.PositiveIntegerField(null=True, blank=True, verbose_name='Год основания')
    address = models.CharField(max_length=255, blank=True, verbose_name='Адрес')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    requisites = models.TextField(blank=True, verbose_name='Реквизиты')

    class Meta:
        verbose_name = 'Информация о компании'
        verbose_name_plural = 'Информация о компании'

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=300, verbose_name='Заголовок')
    summary = models.CharField(max_length=500, verbose_name='Краткое описание')
    content = models.TextField(verbose_name='Содержание')
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name='Изображение')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Автор')
    published_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    is_published = models.BooleanField(default=True, verbose_name='Опубликована')

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class GlossaryTerm(models.Model):
    question = models.CharField(max_length=300, verbose_name='Вопрос')
    answer = models.TextField(verbose_name='Ответ')
    added_at = models.DateField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Термин словаря'
        verbose_name_plural = 'Словарь терминов'
        ordering = ['-added_at']

    def __str__(self):
        return self.question


class StaffContact(models.Model):
    full_name = models.CharField(max_length=200, verbose_name='ФИО')
    position = models.CharField(max_length=200, verbose_name='Должность')
    description = models.TextField(blank=True, verbose_name='Описание работ')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    photo = models.ImageField(upload_to='staff/', blank=True, null=True, verbose_name='Фото')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Контакт сотрудника'
        verbose_name_plural = 'Контакты сотрудников'
        ordering = ['order']

    def __str__(self):
        return f'{self.full_name} — {self.position}'


class Vacancy(models.Model):
    title = models.CharField(max_length=200, verbose_name='Должность')
    description = models.TextField(verbose_name='Описание')
    salary = models.CharField(max_length=100, blank=True, verbose_name='Зарплата')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name='Оценка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Отзыв от {self.user.username} ({self.rating}/5)'


class PromoCode(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('archive', 'Архивный'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name='Код')
    description = models.TextField(verbose_name='Описание')
    discount_percent = models.PositiveSmallIntegerField(verbose_name='Скидка %')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name='Статус')
    valid_from = models.DateField(verbose_name='Действует с')
    valid_to = models.DateField(verbose_name='Действует до')

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды и купоны'

    def __str__(self):
        return f'{self.code} ({self.discount_percent}%)'

