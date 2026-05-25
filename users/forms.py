from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile, validate_phone, validate_age_18


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label='Имя')
    last_name = forms.CharField(max_length=50, required=True, label='Фамилия')
    email = forms.EmailField(required=True, label='Email')
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Дата рождения',
        validators=[validate_age_18],
    )
    phone = forms.CharField(
        max_length=20,
        label='Телефон',
        help_text='Формат: +375 (29) XXX-XX-XX',
        validators=[validate_phone],
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        label='Роль',
        initial='buyer',
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        validate_phone(phone)
        return phone

    def clean_birth_date(self):
        bd = self.cleaned_data.get('birth_date')
        if bd:
            validate_age_18(bd)
        return bd


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput())


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=False, label='Имя')
    last_name = forms.CharField(max_length=50, required=False, label='Фамилия')
    email = forms.EmailField(required=False, label='Email')

    class Meta:
        model = UserProfile
        fields = ('birth_date', 'phone', 'address', 'city', 'avatar')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'birth_date': 'Дата рождения',
            'phone': 'Телефон (+375 (29) XXX-XX-XX)',
            'address': 'Адрес',
            'city': 'Город',
            'avatar': 'Аватар',
        }
