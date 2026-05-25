import logging
import calendar
from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Article, CompanyInfo, GlossaryTerm, StaffContact, Vacancy, Review, PromoCode
from django import forms

logger = logging.getLogger('main')


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('text', 'rating')
        labels = {'text': 'Текст отзыва', 'rating': 'Оценка'}
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.Select(choices=Review.RATING_CHOICES),
        }


def home_view(request):
    latest = Article.objects.filter(is_published=True).first()
    now_utc = timezone.now()
    # Python-generated text calendar for current month
    cal = calendar.TextCalendar(firstweekday=0)
    py_calendar = cal.formatmonth(now_utc.year, now_utc.month)
    return render(request, 'main/home.html', {
        'latest': latest,
        'now_utc': now_utc,
        'py_calendar': py_calendar,
    })


def about_view(request):
    company = CompanyInfo.objects.first()
    return render(request, 'main/about.html', {'company': company})


def news_list_view(request):
    articles = Article.objects.filter(is_published=True)
    return render(request, 'main/news_list.html', {'articles': articles})


def article_detail_view(request, pk):
    article = get_object_or_404(Article, pk=pk, is_published=True)
    return render(request, 'main/article_detail.html', {'article': article})


def glossary_view(request):
    terms = GlossaryTerm.objects.all()
    return render(request, 'main/glossary.html', {'terms': terms})


def contacts_view(request):
    staff = StaffContact.objects.all()
    return render(request, 'main/contacts.html', {'staff': staff})


def privacy_view(request):
    return render(request, 'main/privacy.html')


def vacancies_view(request):
    vacancies = Vacancy.objects.filter(is_active=True)
    return render(request, 'main/vacancies.html', {'vacancies': vacancies})


def reviews_view(request):
    reviews = Review.objects.select_related('user').all()
    form = None
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.save()
                logger.info(f'Review added by {request.user.username}')
                messages.success(request, 'Отзыв добавлен!')
                return redirect('reviews')
        else:
            form = ReviewForm()
    return render(request, 'main/reviews.html', {'reviews': reviews, 'form': form})


def promo_view(request):
    active = PromoCode.objects.filter(status='active')
    archive = PromoCode.objects.filter(status='archive')
    return render(request, 'main/promo.html', {'active_promos': active, 'archive_promos': archive})

