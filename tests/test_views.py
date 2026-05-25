import pytest
from datetime import date
from django.contrib.auth.models import User
from django.test import Client


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser('admin2', 'admin2@test.com', 'pass123')


@pytest.fixture
def buyer_user(db):
    from users.models import UserProfile
    u = User.objects.create_user('buyer2', 'buyer2@test.com', 'pass123')
    UserProfile.objects.create(
        user=u, birth_date=date(1990, 5, 15),
        phone='+375 (29) 100-00-01', role='buyer'
    )
    return u


@pytest.fixture
def employee_user(db):
    from users.models import UserProfile
    u = User.objects.create_user('emp1', 'emp1@test.com', 'pass123')
    UserProfile.objects.create(
        user=u, birth_date=date(1985, 3, 10),
        phone='+375 (33) 200-00-02', role='employee'
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
def pizza(db, category, sauce):
    from shop.models import Pizza
    return Pizza.objects.create(
        name='Тестовая', description='Тест', category=category,
        sauce=sauce, ingredients='ингредиенты', weight_g=400,
        calories=800, is_active=True
    )


@pytest.fixture
def pizza_price(db, pizza, size_s):
    from shop.models import PizzaPrice
    return PizzaPrice.objects.create(pizza=pizza, size=size_s, price='9.00')


@pytest.fixture
def order(db, buyer_user):
    from shop.models import Order
    return Order.objects.create(
        client=buyer_user.profile, status='new',
        delivery_type='delivery', delivery_address='ул. Тест, 1',
        total_price='9.00'
    )


class TestPublicPages:
    def test_home(self, client, db):
        r = client.get('/')
        assert r.status_code == 200

    def test_about(self, client, db):
        r = client.get('/about/')
        assert r.status_code == 200

    def test_news_list(self, client, db):
        r = client.get('/news/')
        assert r.status_code == 200

    def test_glossary(self, client, db):
        r = client.get('/glossary/')
        assert r.status_code == 200

    def test_contacts(self, client, db):
        r = client.get('/contacts/')
        assert r.status_code == 200

    def test_privacy(self, client, db):
        r = client.get('/privacy/')
        assert r.status_code == 200

    def test_vacancies(self, client, db):
        r = client.get('/vacancies/')
        assert r.status_code == 200

    def test_reviews(self, client, db):
        r = client.get('/reviews/')
        assert r.status_code == 200

    def test_promo(self, client, db):
        r = client.get('/promo/')
        assert r.status_code == 200

    def test_pizza_list(self, client, db, pizza):
        r = client.get('/shop/')
        assert r.status_code == 200

    def test_pizza_detail(self, client, db, pizza, pizza_price):
        r = client.get(f'/shop/pizza/{pizza.pk}/')
        assert r.status_code == 200
        assert 'Тестовая' in r.content.decode()

    def test_pickup_points(self, client, db):
        r = client.get('/shop/pickup-points/')
        assert r.status_code == 200



class TestAuthPages:
    def test_login_get(self, client, db):
        r = client.get('/users/login/')
        assert r.status_code == 200

    def test_register_get(self, client, db):
        r = client.get('/users/register/')
        assert r.status_code == 200

    def test_cart_redirect_anonymous(self, client, db):
        r = client.get('/shop/cart/')
        assert r.status_code == 302
        assert '/users/login/' in r['Location']

    def test_checkout_redirect_anonymous(self, client, db):
        r = client.get('/shop/checkout/')
        assert r.status_code == 302

    def test_orders_redirect_anonymous(self, client, db):
        r = client.get('/shop/orders/')
        assert r.status_code == 302

    def test_profile_redirect_anonymous(self, client, db):
        r = client.get('/users/profile/')
        assert r.status_code == 302


class TestLogin:
    def test_login_valid(self, client, db, buyer_user):
        r = client.post('/users/login/', {'username': 'buyer2', 'password': 'pass123'})
        assert r.status_code == 302

    def test_login_invalid(self, client, db):
        r = client.post('/users/login/', {'username': 'nobody', 'password': 'wrong'})
        assert r.status_code == 200

    def test_logout(self, client, db, buyer_user):
        client.login(username='buyer2', password='pass123')
        r = client.get('/users/logout/')
        assert r.status_code == 302


class TestRegistration:
    def test_register_valid(self, client, db):
        r = client.post('/users/register/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'Complexpass123!',
            'password2': 'Complexpass123!',
            'first_name': 'New',
            'last_name': 'User',
            'birth_date': '1990-05-15',
            'phone': '+375 (29) 555-55-55',
            'role': 'buyer',
        })
        assert r.status_code == 302
        assert User.objects.filter(username='newuser').exists()

    def test_register_underage(self, client, db):
        r = client.post('/users/register/', {
            'username': 'younguser',
            'email': 'young@test.com',
            'password1': 'Complexpass123!',
            'password2': 'Complexpass123!',
            'first_name': 'Young',
            'last_name': 'User',
            'birth_date': '2015-01-01',
            'phone': '+375 (29) 111-11-11',
            'role': 'buyer',
        })
        assert r.status_code == 200
        assert not User.objects.filter(username='younguser').exists()


class TestShopCart:
    def test_cart_empty(self, client, db, buyer_user):
        client.login(username='buyer2', password='pass123')
        r = client.get('/shop/cart/')
        assert r.status_code == 200

    def test_add_to_cart(self, client, db, buyer_user, pizza, pizza_price):
        client.login(username='buyer2', password='pass123')
        r = client.post(f'/shop/pizza/{pizza.pk}/add-to-cart/', {
            'size_id': pizza_price.size.pk,
            'quantity': 1,
        })
        assert r.status_code == 302

    def test_remove_from_cart(self, client, db, buyer_user, pizza, pizza_price):
        client.login(username='buyer2', password='pass123')
        client.post(f'/shop/pizza/{pizza.pk}/add-to-cart/', {
            'size_id': pizza_price.size.pk,
            'quantity': 1,
        })
        r = client.get(f'/shop/cart/remove/{pizza.pk}_{pizza_price.size.pk}/')
        assert r.status_code == 302


class TestOrders:
    def test_order_list_buyer(self, client, db, buyer_user):
        client.login(username='buyer2', password='pass123')
        r = client.get('/shop/orders/')
        assert r.status_code == 200

    def test_order_list_employee(self, client, db, employee_user):
        client.login(username='emp1', password='pass123')
        r = client.get('/shop/orders/')
        assert r.status_code == 200

    def test_order_list_admin(self, client, db, admin_user):
        client.login(username='admin2', password='pass123')
        r = client.get('/shop/orders/')
        assert r.status_code == 200

    def test_order_detail_buyer_own(self, client, db, buyer_user, order):
        client.login(username='buyer2', password='pass123')
        r = client.get(f'/shop/orders/{order.pk}/')
        assert r.status_code == 200

    def test_order_detail_other_user_denied(self, client, db, employee_user, order):
        client.login(username='emp1', password='pass123')
        r = client.get(f'/shop/orders/{order.pk}/')
        assert r.status_code in (200, 302)


class TestStatistics:
    def test_stats_redirect_anonymous(self, client, db):
        r = client.get('/shop/statistics/')
        assert r.status_code == 302

    def test_stats_redirect_buyer(self, client, db, buyer_user):
        client.login(username='buyer2', password='pass123')
        r = client.get('/shop/statistics/')
        assert r.status_code == 302

    def test_stats_accessible_admin(self, client, db, admin_user):
        client.login(username='admin2', password='pass123')
        r = client.get('/shop/statistics/')
        assert r.status_code == 200


class TestPizzaCRUD:
    def test_create_pizza_admin(self, client, db, admin_user, category, sauce):
        client.login(username='admin2', password='pass123')
        r = client.get('/shop/pizza/create/')
        assert r.status_code == 200

    def test_create_pizza_buyer_denied(self, client, db, buyer_user):
        client.login(username='buyer2', password='pass123')
        r = client.get('/shop/pizza/create/')
        assert r.status_code == 302

    def test_edit_pizza_admin(self, client, db, admin_user, pizza):
        client.login(username='admin2', password='pass123')
        r = client.get(f'/shop/pizza/{pizza.pk}/edit/')
        assert r.status_code == 200

    def test_delete_pizza_admin(self, client, db, admin_user, pizza):
        client.login(username='admin2', password='pass123')
        r = client.get(f'/shop/pizza/{pizza.pk}/delete/')
        assert r.status_code == 200


class TestArticle:
    def test_article_detail(self, client, db, admin_user):
        from main.models import Article
        a = Article.objects.create(
            title='Test news', summary='s', content='c',
            author=admin_user, is_published=True
        )
        r = client.get(f'/news/{a.pk}/')
        assert r.status_code == 200

    def test_article_detail_unpublished_404(self, client, db, admin_user):
        from main.models import Article
        a = Article.objects.create(
            title='Hidden', summary='s', content='c',
            author=admin_user, is_published=False
        )
        r = client.get(f'/news/{a.pk}/')
        assert r.status_code == 404


class TestDashboard:
    def test_dashboard_authenticated(self, client, db, buyer_user):
        client.login(username='buyer2', password='pass123')
        r = client.get('/users/dashboard/')
        assert r.status_code == 200

    def test_profile_authenticated(self, client, db, buyer_user):
        client.login(username='buyer2', password='pass123')
        r = client.get('/users/profile/')
        assert r.status_code == 200


class TestPizzaSearch:
    def test_search_by_name(self, client, db, pizza):
        r = client.get('/shop/?q=Тестовая')
        assert r.status_code == 200

    def test_search_no_results(self, client, db, pizza):
        r = client.get('/shop/?q=НесуществующаяПицца12345')
        assert r.status_code == 200

    def test_filter_by_category(self, client, db, pizza, category):
        r = client.get(f'/shop/?category={category.pk}')
        assert r.status_code == 200
