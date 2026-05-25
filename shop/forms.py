from django import forms
from .models import Pizza, PizzaCategory, Sauce


class PizzaForm(forms.ModelForm):
    class Meta:
        model = Pizza
        fields = ('name', 'description', 'image', 'category', 'sauce', 'ingredients', 'weight_g', 'calories', 'is_active')
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'image': 'Фото',
            'category': 'Категория',
            'sauce': 'Соус',
            'ingredients': 'Состав',
            'weight_g': 'Вес (г)',
            'calories': 'Калории',
            'is_active': 'В продаже',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'ingredients': forms.Textarea(attrs={'rows': 2}),
        }


class PizzaSearchForm(forms.Form):
    sauce = forms.ModelChoiceField(
        queryset=Sauce.objects.all(),
        required=False,
        empty_label='Любой соус',
        label='Соус',
    )
    category = forms.ModelChoiceField(
        queryset=PizzaCategory.objects.all(),
        required=False,
        empty_label='Любая категория',
        label='Категория',
    )
    min_price = forms.DecimalField(required=False, min_value=0, label='Цена от')
    max_price = forms.DecimalField(required=False, min_value=0, label='Цена до')
    q = forms.CharField(required=False, label='Поиск')
