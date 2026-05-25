import pytest
from datetime import date
from django.contrib.auth.models import User
from django.test import Client


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser('apiadmin', 'apiadmin@test.com', 'pass123')


@pytest.fixture
def regular_user(db):
    from users.models import UserProfile
    u = User.objects.create_user('apiuser', 'apiuser@test.com', 'pass123')
    UserProfile.objects.create(
        user=u, birth_date=date(1990, 1, 1),
        phone='+375 (29) 777-88-99', role='buyer'
    )
    return u


class TestWeatherAPI:
    def test_weather_accessible_anonymous(self, client, db):
        r = client.get('/api/weather/?city=Minsk')
        assert r.status_code in (200, 503)

    def test_weather_returns_json(self, client, db):
        r = client.get('/api/weather/?city=Minsk')
        assert r['Content-Type'].startswith('application/json')


class TestCurrencyAPI:
    def test_currency_accessible_anonymous(self, client, db):
        r = client.get('/api/currency/?base=USD')
        assert r.status_code in (200, 503)

    def test_currency_returns_json(self, client, db):
        r = client.get('/api/currency/?base=USD')
        assert r['Content-Type'].startswith('application/json')


class TestPizzasAPI:
    def test_pizzas_requires_auth(self, client, db):
        r = client.get('/api/pizzas/')
        assert r.status_code == 403

    def test_pizzas_authenticated(self, client, db, regular_user):
        client.login(username='apiuser', password='pass123')
        r = client.get('/api/pizzas/')
        assert r.status_code == 200

    def test_pizzas_returns_list(self, client, db, regular_user):
        client.login(username='apiuser', password='pass123')
        r = client.get('/api/pizzas/')
        assert isinstance(r.json(), list)


class TestOrdersAPI:
    def test_orders_requires_auth(self, client, db):
        r = client.get('/api/orders/')
        assert r.status_code == 403

    def test_orders_requires_superuser(self, client, db, regular_user):
        client.login(username='apiuser', password='pass123')
        r = client.get('/api/orders/')
        assert r.status_code == 403

    def test_orders_accessible_admin(self, client, db, admin_user):
        client.login(username='apiadmin', password='pass123')
        r = client.get('/api/orders/')
        assert r.status_code == 200


class TestStatsAPI:
    def test_stats_requires_auth(self, client, db):
        r = client.get('/api/stats/')
        assert r.status_code == 403

    def test_stats_requires_superuser(self, client, db, regular_user):
        client.login(username='apiuser', password='pass123')
        r = client.get('/api/stats/')
        assert r.status_code == 403

    def test_stats_accessible_admin(self, client, db, admin_user):
        client.login(username='apiadmin', password='pass123')
        r = client.get('/api/stats/')
        assert r.status_code == 200
        data = r.json()
        assert 'total_orders' in data
        assert 'total_revenue' in data
