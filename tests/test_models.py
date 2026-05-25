import pytest
from datetime import date
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser('testadmin', 'admin@test.com', 'pass123')


@pytest.fixture
def regular_user(db):
    from users.models import UserProfile
    u = User.objects.create_user('testuser', 'user@test.com', 'pass123',
                                  first_name='Test', last_name='User')
    UserProfile.objects.create(
        user=u, birth_date=date(1990, 1, 1),
        phone='+375 (29) 123-45-67', role='buyer'
    )
    return u


@pytest.fixture
def sauce(db):
    from shop.models import Sauce
    return Sauce.objects.create(name='Томатный')


@pytest.fixture
def category(db):
    from shop.models import PizzaCategory
    return PizzaCategory.objects.create(name='Классическая')


@pytest.fixture
def size_s(db):
    from shop.models import PizzaSize
    return PizzaSize.objects.create(name='S', diameter_cm=25)


@pytest.fixture
def size_m(db):
    from shop.models import PizzaSize
    return PizzaSize.objects.create(name='M', diameter_cm=30)


@pytest.fixture
def pizza(db, category, sauce):
    from shop.models import Pizza
    return Pizza.objects.create(
        name='Маргарита', description='Классика', category=category,
        sauce=sauce, ingredients='томат, моцарелла', weight_g=400,
        calories=800, is_active=True
    )


@pytest.fixture
def pizza_price(db, pizza, size_s):
    from shop.models import PizzaPrice
    return PizzaPrice.objects.create(pizza=pizza, size=size_s, price='8.50')


@pytest.fixture
def user_profile(db, regular_user):
    return regular_user.profile


@pytest.fixture
def order(db, user_profile):
    from shop.models import Order
    return Order.objects.create(
        client=user_profile, status='new',
        delivery_type='delivery',
        delivery_address='ул. Тестовая, 1',
        total_price='12.00'
    )


class TestPhoneValidation:
    def test_valid_phone(self, db):
        from users.models import validate_phone
        validate_phone('+375 (29) 123-45-67')
        validate_phone('+375 (33) 999-88-77')
        validate_phone('+375 (44) 000-11-22')
        validate_phone('+375 (25) 333-44-55')

    def test_invalid_phone(self, db):
        from users.models import validate_phone
        with pytest.raises(ValidationError):
            validate_phone('375 29 1234567')
        with pytest.raises(ValidationError):
            validate_phone('+375(29)1234567')
        with pytest.raises(ValidationError):
            validate_phone('+375 (28) 123-45-67')


class TestAgeValidation:
    def test_valid_age(self, db):
        from users.models import validate_age_18
        validate_age_18(date(1990, 1, 1))
        validate_age_18(date(2000, 1, 1))

    def test_invalid_age(self, db):
        from users.models import validate_age_18
        young = date.today().replace(year=date.today().year - 17)
        with pytest.raises(ValidationError):
            validate_age_18(young)


class TestUserProfile:
    def test_profile_str(self, db, user_profile):
        s = str(user_profile)
        assert 'Test User' in s or 'testuser' in s

    def test_profile_role_default(self, db, regular_user):
        assert regular_user.profile.role == 'buyer'


class TestPizzaModel:
    def test_pizza_str(self, db, pizza):
        assert 'Маргарита' in str(pizza)

    def test_get_min_price_no_prices(self, db, pizza):
        assert pizza.get_min_price() == 0

    def test_get_min_price_with_prices(self, db, pizza, pizza_price, size_m):
        from shop.models import PizzaPrice
        PizzaPrice.objects.create(pizza=pizza, size=size_m, price='12.00')
        assert float(pizza.get_min_price()) == 8.50

    def test_pizza_size_str(self, db, size_s):
        assert 'S' in str(size_s)

    def test_pizza_price_str(self, db, pizza_price):
        assert 'Маргарита' in str(pizza_price)


class TestOrderModel:
    def test_order_str(self, db, order):
        assert str(order.pk) in str(order)

    def test_order_status_default(self, db, order):
        assert order.status == 'new'

    def test_order_item(self, db, order, pizza, size_s):
        from shop.models import OrderItem
        from decimal import Decimal
        item = OrderItem.objects.create(
            order=order, pizza=pizza, size=size_s,
            quantity=2, unit_price=Decimal('8.50')
        )
        assert item.get_subtotal() == Decimal('17.00')


class TestMainModels:
    def test_article(self, db, admin_user):
        from main.models import Article
        a = Article.objects.create(
            title='Test', summary='s', content='c', author=admin_user
        )
        assert 'Test' in str(a)

    def test_glossary_term(self, db):
        from main.models import GlossaryTerm
        g = GlossaryTerm.objects.create(question='Q?', answer='A')
        assert 'Q?' in str(g)

    def test_review(self, db, admin_user):
        from main.models import Review
        r = Review.objects.create(user=admin_user, text='Great!', rating=5)
        assert 'admin' in str(r)

    def test_promo_code(self, db):
        from main.models import PromoCode
        p = PromoCode.objects.create(
            code='TEST10', description='Test', discount_percent=10,
            status='active', valid_from=date.today(),
            valid_to=date.today()
        )
        assert 'TEST10' in str(p)

    def test_vacancy(self, db):
        from main.models import Vacancy
        v = Vacancy.objects.create(title='Courier', description='Fast', salary='500')
        assert 'Courier' in str(v)

    def test_company_info(self, db):
        from main.models import CompanyInfo
        c = CompanyInfo.objects.create(name='Test Co', description='Desc')
        assert 'Test Co' in str(c)
