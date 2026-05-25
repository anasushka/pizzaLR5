from django.contrib import admin
from .models import CompanyInfo, Article, GlossaryTerm, StaffContact, Vacancy, Review, PromoCode


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('title', 'summary', 'content')
    list_editable = ('is_published',)
    date_hierarchy = 'published_at'


@admin.register(GlossaryTerm)
class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ('question', 'added_at')
    search_fields = ('question', 'answer')
    date_hierarchy = 'added_at'


@admin.register(StaffContact)
class StaffContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'phone', 'email', 'order')
    list_editable = ('order',)
    search_fields = ('full_name', 'position')


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'salary', 'is_active', 'created_at')
    list_filter = ('is_active',)
    list_editable = ('is_active',)
    search_fields = ('title', 'description')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__username', 'text')
    date_hierarchy = 'created_at'


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'status', 'valid_from', 'valid_to')
    list_filter = ('status',)
    list_editable = ('status',)
    search_fields = ('code', 'description')

