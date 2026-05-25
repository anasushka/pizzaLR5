"""
Management command: python manage.py seed_data
Creates 10+ demo records in every table.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Seed the database with 10+ demo records per table'

    def handle(self, *args, **options):
        self._seed_users()
        self._seed_shop()
        self._seed_main()
        self._seed_orders()
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

    def _seed_users(self):
        from users.models import UserProfile

        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@pizzahouse.by', 'admin123')
            self.stdout.write('Created superuser: admin / admin123')

        demo_users = [
            ('ivan',      'ivan@example.com',     'pass1234', 'Иван',      'Петров',    '1990-05-15', '+375 (29) 123-45-67', 'buyer'),
            ('anna',      'anna@example.com',     'pass1234', 'Анна',      'Сидорова',  '1995-03-22', '+375 (33) 987-65-43', 'buyer'),
            ('sergei',    'sergei@example.com',   'pass1234', 'Сергей',    'Козлов',    '1988-07-10', '+375 (44) 111-22-33', 'buyer'),
            ('maria',     'maria@example.com',    'pass1234', 'Мария',     'Иванова',   '1993-12-01', '+375 (29) 234-56-78', 'buyer'),
            ('dmitry',    'dmitry@example.com',   'pass1234', 'Дмитрий',   'Волков',    '1985-09-20', '+375 (33) 345-67-89', 'buyer'),
            ('elena',     'elena@example.com',    'pass1234', 'Елена',     'Новикова',  '1992-04-18', '+375 (44) 456-78-90', 'buyer'),
            ('alexei',    'alexei@example.com',   'pass1234', 'Алексей',   'Соколов',   '1987-11-03', '+375 (25) 567-89-01', 'buyer'),
            ('courier1',  'c1@example.com',       'pass1234', 'Дмитрий',   'Ковалёв',   '1988-11-01', '+375 (44) 100-20-30', 'employee'),
            ('courier2',  'c2@example.com',       'pass1234', 'Николай',   'Романов',   '1991-06-15', '+375 (29) 200-30-40', 'employee'),
            ('courier3',  'c3@example.com',       'pass1234', 'Юрий',      'Морозов',   '1994-02-28', '+375 (33) 300-40-50', 'employee'),
            ('courier4',  'c4@example.com',       'pass1234', 'Виктор',    'Зайцев',    '1989-08-12', '+375 (44) 400-50-60', 'employee'),
            ('courier5',  'c5@example.com',       'pass1234', 'Павел',     'Белов',     '1993-03-05', '+375 (29) 500-60-70', 'employee'),
            ('courier6',  'c6@example.com',       'pass1234', 'Илья',      'Попов',     '1987-01-20', '+375 (33) 600-70-80', 'employee'),
            ('courier7',  'c7@example.com',       'pass1234', 'Максим',    'Лебедев',   '1996-07-14', '+375 (44) 700-80-90', 'employee'),
            ('courier8',  'c8@example.com',       'pass1234', 'Роман',     'Кузнецов',  '1990-11-25', '+375 (29) 800-90-01', 'employee'),
            ('courier9',  'c9@example.com',       'pass1234', 'Артём',     'Смирнов',   '1992-05-18', '+375 (33) 900-01-12', 'employee'),
            ('courier10', 'c10@example.com',      'pass1234', 'Евгений',   'Орлов',     '1986-09-07', '+375 (44) 010-11-22', 'employee'),
        ]
        for username, email, password, first, last, bday, phone, role in demo_users:
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(username, email, password, first_name=first, last_name=last)
                UserProfile.objects.create(
                    user=u,
                    birth_date=date.fromisoformat(bday),
                    phone=phone,
                    role=role,
                )
                self.stdout.write(f'Created user: {username}')

    def _seed_shop(self):
        from shop.models import (
            Sauce, PizzaCategory, PizzaSize, Pizza, PizzaPrice,
            PickupPoint, Courier, Ingredient
        )
        from users.models import UserProfile

        sauce_names = [
            'Томатный', 'Сливочный', 'Барбекю', 'Острый чили', 'Песто',
            'Грибной', 'Сырный', 'Чесночный', 'Медово-горчичный', 'Ранч',
        ]
        sauces = {}
        for name in sauce_names:
            obj, _ = Sauce.objects.get_or_create(name=name)
            sauces[name] = obj

        category_names = [
            'Классическая', 'Острая', 'Вегетарианская', 'Мясная', 'Морепродукты',
            'Сырная', 'Постная', 'Детская', 'Фирменная', 'Сезонная',
        ]
        categories = {}
        for name in category_names:
            obj, _ = PizzaCategory.objects.get_or_create(name=name)
            categories[name] = obj

        sizes = {}
        for name, diameter in [('S', 25), ('M', 30), ('L', 35), ('XL', 40)]:
            obj, _ = PizzaSize.objects.get_or_create(name=name, defaults={'diameter_cm': diameter})
            sizes[name] = obj

        ingredient_names = [
            ('Моцарелла', 0), ('Пепперони', 1.50), ('Грибы', 0.80),
            ('Ветчина', 1.20), ('Оливки', 0.70), ('Томаты', 0.50),
            ('Базилик', 0.30), ('Руккола', 0.40), ('Бекон', 1.30), ('Ананас', 0.90),
        ]
        for name, price in ingredient_names:
            Ingredient.objects.get_or_create(name=name, defaults={'price_extra': price})

        pizzas_data = [
            ('Маргарита',      'Классическая итальянская с моцареллой и базиликом',
             'Классическая',  'Томатный',        'томатный соус, моцарелла, базилик',                      400, 800,
             {'S': 8.50, 'M': 12.00, 'L': 15.50, 'XL': 19.00}),
            ('Пепперони',      'Острая пицца с пикантной колбасой',
             'Острая',        'Томатный',        'томатный соус, моцарелла, пепперони',                    450, 950,
             {'S': 9.50, 'M': 13.50, 'L': 17.00, 'XL': 21.00}),
            ('Четыре сыра',    'Сливочная пицца с ассорти из четырёх видов сыра',
             'Сырная',        'Сливочный',       'сливочный соус, моцарелла, пармезан, горгонзола, чеддер', 480, 1100,
             {'S': 11.00, 'M': 15.00, 'L': 19.00, 'XL': 23.00}),
            ('Барбекю',        'Сочная мясная пицца с соусом барбекю и курицей',
             'Мясная',        'Барбекю',         'соус барбекю, куриное филе, красный лук, моцарелла',     500, 1050,
             {'S': 10.00, 'M': 14.00, 'L': 18.00, 'XL': 22.00}),
            ('Вегетарианская', 'Лёгкая пицца с овощами и зеленью',
             'Вегетарианская','Томатный',        'томатный соус, моцарелла, болгарский перец, грибы, оливки', 380, 700,
             {'S': 8.00, 'M': 11.50, 'L': 15.00, 'XL': 18.50}),
            ('Гавайская',      'Сладко-солёная с курицей и ананасом',
             'Классическая',  'Томатный',        'томатный соус, куриное филе, ананас, моцарелла',         430, 880,
             {'S': 9.00, 'M': 12.50, 'L': 16.00, 'XL': 20.00}),
            ('Морская',        'Изысканная пицца с морепродуктами',
             'Морепродукты',  'Сливочный',       'сливочный соус, креветки, мидии, кальмар, моцарелла',    420, 820,
             {'S': 13.00, 'M': 17.50, 'L': 22.00, 'XL': 27.00}),
            ('Мясная',         'Сытная пицца с несколькими видами мяса',
             'Мясная',        'Барбекю',         'соус барбекю, говядина, курица, бекон, моцарелла',       550, 1200,
             {'S': 12.00, 'M': 16.50, 'L': 21.00, 'XL': 25.50}),
            ('Острая чили',    'Очень острая пицца для любителей жгучего',
             'Острая',        'Острый чили',     'острый соус, пепперони, перец халапеньо, моцарелла',     440, 920,
             {'S': 9.50, 'M': 13.00, 'L': 16.50, 'XL': 20.50}),
            ('Грибная',        'Ароматная пицца с лесными грибами',
             'Вегетарианская','Грибной',         'грибной соус, белые грибы, шампиньоны, моцарелла, тимьян', 410, 830,
             {'S': 9.00, 'M': 12.50, 'L': 16.00, 'XL': 19.50}),
            ('Карбонара',      'Итальянская классика с беконом и яичным соусом',
             'Классическая',  'Сливочный',       'сливочный соус, бекон, яйцо, пармезан, моцарелла',      470, 980,
             {'S': 10.50, 'M': 14.50, 'L': 18.50, 'XL': 22.50}),
            ('Песто',          'Ароматная пицца с соусом песто и вялеными томатами',
             'Постная',       'Песто',           'соус песто, вяленые томаты, руккола, пармезан',          360, 750,
             {'S': 10.00, 'M': 14.00, 'L': 17.50, 'XL': 21.00}),
            ('Фирменная',      'Фирменный рецепт шеф-повара с трюфельным маслом',
             'Фирменная',     'Сырный',          'сырный соус, трюфельное масло, пармезан, руккола',       390, 860,
             {'S': 14.00, 'M': 19.00, 'L': 24.00, 'XL': 29.00}),
            ('Детская',        'Нежная пицца для самых маленьких гостей',
             'Детская',       'Томатный',        'томатный соус, моцарелла, курица, кукуруза',             350, 680,
             {'S': 7.50, 'M': 10.50, 'L': 13.50, 'XL': 17.00}),
            ('Сезонная',       'Специальное предложение сезона с сезонными овощами',
             'Сезонная',      'Чесночный',       'чесночный соус, сезонные овощи, козий сыр, моцарелла',  420, 810,
             {'S': 11.50, 'M': 15.50, 'L': 19.50, 'XL': 24.00}),
        ]

        for name, desc, cat, sauce, ingr, weight, cal, price_map in pizzas_data:
            pizza, created = Pizza.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'category': categories[cat],
                    'sauce': sauces[sauce],
                    'ingredients': ingr,
                    'weight_g': weight,
                    'calories': cal,
                    'is_active': True,
                }
            )
            if created:
                for size_name, price in price_map.items():
                    PizzaPrice.objects.get_or_create(pizza=pizza, size=sizes[size_name], defaults={'price': price})
        self.stdout.write(f'Seeded {len(pizzas_data)} pizzas')

        pickup_data = [
            ('PizzaHouse Центр',   'г. Минск, пр. Независимости, 25',  '+375 (17) 200-10-10', 'Пн–Вс 10:00–22:00'),
            ('PizzaHouse Запад',   'г. Минск, ул. Притыцкого, 50',     '+375 (17) 355-20-20', 'Пн–Вс 11:00–21:00'),
            ('PizzaHouse Восток',  'г. Минск, ул. Ташкентская, 1',     '+375 (17) 222-30-30', 'Пт–Вс 12:00–23:00'),
            ('PizzaHouse Север',   'г. Минск, ул. Скорины, 14',        '+375 (17) 333-44-55', 'Пн–Вс 10:00–22:00'),
            ('PizzaHouse Юг',      'г. Минск, ул. Партизанская, 78',   '+375 (17) 444-55-66', 'Пн–Пт 11:00–21:00'),
            ('PizzaHouse Центр-2', 'г. Минск, ул. Немига, 5',          '+375 (17) 555-66-77', 'Пн–Вс 09:00–23:00'),
            ('PizzaHouse Малиновка', 'г. Минск, пр. Дзержинского, 100', '+375 (17) 666-77-88', 'Пн–Вс 10:00–22:00'),
            ('PizzaHouse Уручье',  'г. Минск, ул. Городецкая, 20',     '+375 (17) 777-88-99', 'Пн–Пт 11:00–21:00'),
            ('PizzaHouse Каменная Горка', 'г. Минск, ул. Лобанка, 33', '+375 (17) 888-99-00', 'Пн–Вс 10:00–22:00'),
            ('PizzaHouse Сухарево', 'г. Минск, ул. Лещинского, 7',    '+375 (17) 999-00-11', 'Пн–Пт 10:00–21:00'),
        ]
        for name, address, phone, hours in pickup_data:
            PickupPoint.objects.get_or_create(
                name=name,
                defaults={'address': address, 'phone': phone, 'working_hours': hours, 'is_active': True}
            )

        courier_users = ['courier1','courier2','courier3','courier4','courier5',
                         'courier6','courier7','courier8','courier9','courier10']
        vehicles = ['Велосипед','Мотоцикл','Электросамокат','Мотоцикл','Велосипед',
                    'Электросамокат','Мотоцикл','Велосипед','Мотоцикл','Электросамокат']
        for uname, vehicle in zip(courier_users, vehicles):
            try:
                profile = UserProfile.objects.get(user__username=uname)
                Courier.objects.get_or_create(
                    profile=profile,
                    defaults={'vehicle': vehicle, 'is_available': True}
                )
            except UserProfile.DoesNotExist:
                pass

    def _seed_main(self):
        from main.models import CompanyInfo, Article, GlossaryTerm, StaffContact, Vacancy, PromoCode
        from django.contrib.auth.models import User

        CompanyInfo.objects.get_or_create(
            name='PizzaHouse',
            defaults={
                'description': 'Мы — команда энтузиастов, влюблённых в итальянскую кухню. Основанная в 2018 году, PizzaHouse стала любимым местом для тысяч минчан. Мы используем только свежие ингредиенты, готовим тесто вручную каждый день и доставляем пиццу горячей прямо к вашей двери.',
                'founded_year': 2018,
                'address': 'г. Минск, пр. Независимости, 25',
                'phone': '+375 (17) 200-10-10',
                'email': 'info@pizzahouse.by',
                'requisites': 'ООО «ПиццаХаус»\nУНП: 193456789\nр/с BY20ALFA30122162200014550000\nАО «Альфа-Банк», г. Минск',
            }
        )

        admin_user = User.objects.filter(username='admin').first()

        articles = [
            ('Открываем третью точку!',
             'Рады сообщить об открытии нового пункта самовывоза на востоке Минска.',
             'Уже с 1 декабря 2024 года вы сможете забирать горячую пиццу на ул. Ташкентской, 1! Новый пункт оборудован удобной парковкой и быстрой выдачей заказов. Ждём вас!'),
            ('Новинка в меню: Карбонара',
             'Мы добавили в меню классическую итальянскую карбонару!',
             'Тончайшее тесто, нежный сливочный соус, хрустящий бекон и пармезан — именно так звучит наша новая пицца Карбонара. Попробуйте её уже сегодня!'),
            ('Акция: Скидка 20% на первый заказ',
             'Для новых покупателей действует специальная скидка.',
             'Зарегистрируйтесь на сайте и получите промокод WELCOME20 — он даёт скидку 20% на ваш первый заказ. Акция действует до 31 декабря 2024 года.'),
            ('День рождения PizzaHouse!',
             'Нам исполняется 6 лет — отмечаем вместе!',
             'В честь нашего 6-летия мы дарим скидки всем постоянным клиентам. Используйте промокод BIRTHDAY6 до конца месяца. Спасибо, что вы с нами!'),
            ('Новый курьер-робот проходит испытания',
             'Мы тестируем доставку с помощью автономного робота.',
             'В рамках пилотного проекта мы запустили тестирование курьера-робота в центре Минска. Первые 100 заказов доставил без единого сбоя! Следите за новостями.'),
            ('Мастер-класс по приготовлению пиццы',
             'Приглашаем всех желающих научиться готовить настоящую итальянскую пиццу!',
             'Каждую субботу в 11:00 наш шеф-повар проводит мастер-класс. Стоимость — 30 руб. с человека, включает все ингредиенты и готовую пиццу для дегустации.'),
            ('Обновление приложения',
             'Вышло обновление мобильного приложения PizzaHouse.',
             'В новой версии: отслеживание заказа на карте в реальном времени, новые фильтры в меню, быстрый повтор предыдущего заказа. Обновляйтесь в App Store и Google Play!'),
            ('Партнёрство с фермерскими хозяйствами',
             'Теперь все томаты и зелень — только от белорусских фермеров.',
             'Мы заключили договоры с 5 фермерскими хозяйствами. Свежие томаты, базилик и руккола теперь доставляются ежедневно прямо с грядки. Вкус стал ещё лучше!'),
            ('Зимнее меню 2025',
             'Встречайте новые пиццы зимней коллекции!',
             'Специально для холодного сезона: «Трюфельная», «Тыквенная» с козьим сыром и «Зимняя» с грибами и трюфельным маслом. Согревайтесь вкусной пиццей!'),
            ('Экологичная упаковка',
             'С нового года переходим на 100% биоразлагаемую упаковку.',
             'Наши коробки теперь изготовлены из переработанного картона и разлагаются за 6 недель. Вместе заботимся о планете — без ущерба для вкуса!'),
        ]
        for title, summary, content in articles:
            Article.objects.get_or_create(title=title, defaults={
                'summary': summary, 'content': content,
                'author': admin_user, 'is_published': True,
            })

        glossary_terms = [
            ('Что такое моцарелла?',
             'Моцарелла — итальянский сыр из коровьего молока, мягкий и тягучий. Незаменим для пиццы.'),
            ('Что такое пепперони?',
             'Пепперони — острая итальянская колбаса из свинины и говядины, один из самых популярных топпингов.'),
            ('Чем отличается пицца Маргарита от других?',
             'Маргарита — базовая пицца: томатный соус, моцарелла, базилик. Символизирует цвета итальянского флага.'),
            ('Что такое соус песто?',
             'Песто — традиционный итальянский соус из базилика, оливкового масла, чеснока, кедровых орехов и пармезана.'),
            ('Как правильно выбрать размер пиццы?',
             'S (25 см) — на 1 человека, M (30 см) — на 1-2 человека, L (35 см) — на 2-3, XL (40 см) — на 3-4 человека.'),
            ('Что такое тонкое тесто vs. пышное?',
             'Тонкое (неаполитанское) тесто хрустящее по краям, пышное (сицилийское) — мягкое и толстое. Мы готовим тонкое тесто ручной лепки.'),
            ('Что такое бланшировка?',
             'Бланшировка — кратковременная обработка овощей кипятком для сохранения цвета и хрусткости. Применяется для брокколи и болгарского перца в нашей вегетарианской пицце.'),
            ('Что означает «DOP» на продуктах?',
             'DOP (Denominazione di Origine Protetta) — итальянский знак защищённого происхождения. Наша моцарелла DOP производится в Кампании.'),
            ('Что такое трюфельное масло?',
             'Трюфельное масло — оливковое масло с ароматом трюфеля. Придаёт пицце изысканный земляной аромат. Используем в фирменных позициях.'),
            ('Почему пицца круглая?',
             'Круглая форма обеспечивает равномерное пропекание в дровяной печи. При вращении пицца равномерно получает жар со всех сторон.'),
        ]
        for q, a in glossary_terms:
            GlossaryTerm.objects.get_or_create(question=q, defaults={'answer': a})

        staff_contacts = [
            ('Алексей Борисов',   'Генеральный директор',   'Руководит всеми процессами компании', '+375 (29) 100-00-01', 'ceo@pizzahouse.by', 0),
            ('Мария Иванова',     'Шеф-повар',              'Создаёт новые рецепты и контролирует качество', '+375 (29) 100-00-02', 'chef@pizzahouse.by', 1),
            ('Сергей Петров',     'Менеджер доставки',      'Координирует работу курьеров', '+375 (29) 100-00-03', 'delivery@pizzahouse.by', 2),
            ('Татьяна Кузнецова', 'HR-менеджер',            'Подбор и обучение персонала', '+375 (29) 100-00-04', 'hr@pizzahouse.by', 3),
            ('Виктор Романов',    'Технолог',               'Контроль качества ингредиентов и рецептур', '+375 (29) 100-00-05', 'tech@pizzahouse.by', 4),
            ('Ольга Смирнова',    'Менеджер по маркетингу', 'Продвижение бренда и акции', '+375 (29) 100-00-06', 'marketing@pizzahouse.by', 5),
            ('Игорь Козлов',      'IT-администратор',       'Поддержка сайта и программного обеспечения', '+375 (29) 100-00-07', 'it@pizzahouse.by', 6),
            ('Наталья Волкова',   'Бухгалтер',              'Финансовый учёт и отчётность', '+375 (29) 100-00-08', 'finance@pizzahouse.by', 7),
            ('Андрей Новиков',    'Старший пиццайоло',      'Обучение персонала кухни', '+375 (29) 100-00-09', 'kitchen@pizzahouse.by', 8),
            ('Светлана Попова',   'Администратор зала',     'Обслуживание клиентов в торговом зале', '+375 (29) 100-00-10', 'hall@pizzahouse.by', 9),
        ]
        for full_name, position, desc, phone, email, order in staff_contacts:
            StaffContact.objects.get_or_create(full_name=full_name, defaults={
                'position': position, 'description': desc,
                'phone': phone, 'email': email, 'order': order,
            })

        vacancies = [
            ('Курьер на велосипеде',  'Доставка пиццы по центру города. Гибкий график, опыт не требуется.',      'от 600 руб./мес.'),
            ('Пиццайоло',             'Приготовление пиццы по нашим рецептам. Обучение за наш счёт.',             'от 900 руб./мес.'),
            ('Менеджер зала',         'Обслуживание клиентов, приём заказов, контроль качества.',                 'от 750 руб./мес.'),
            ('Курьер на мотоцикле',   'Быстрая доставка по всему городу. Нужны права категории А.',              'от 800 руб./мес.'),
            ('Кассир',                'Работа на кассе, приём оплаты наличными и картой.',                        'от 650 руб./мес.'),
            ('Уборщик',               'Поддержание чистоты в зале и на кухне. Гибкий график.',                   'от 500 руб./мес.'),
            ('Старший смены',         'Управление командой из 5-8 человек, контроль качества.',                   'от 1100 руб./мес.'),
            ('SMM-специалист',        'Ведение социальных сетей, создание контента, реклама.',                    'от 700 руб./мес.'),
            ('Водитель-экспедитор',   'Доставка ингредиентов от поставщиков. Нужны права категории В.',          'от 850 руб./мес.'),
            ('Технолог пищевого производства', 'Разработка рецептур, контроль калорийности и состава.',          'от 1200 руб./мес.'),
        ]
        for title, desc, salary in vacancies:
            Vacancy.objects.get_or_create(title=title, defaults={'description': desc, 'salary': salary, 'is_active': True})

        today = date.today()
        promo_data = [
            ('WELCOME20',  'Скидка 20% на первый заказ для новых покупателей',   20, 'active',  today,               today + timedelta(days=365)),
            ('PIZZA10',    'Скидка 10% при заказе от 3 пицц',                    10, 'active',  today,               today + timedelta(days=90)),
            ('FRIDAY15',   'Пятничная скидка 15%',                               15, 'active',  today,               today + timedelta(days=30)),
            ('BIRTHDAY6',  'Скидка 25% в честь 6-летия PizzaHouse',              25, 'active',  today,               today + timedelta(days=14)),
            ('WINTER10',   'Зимняя скидка 10% на все заказы',                    10, 'active',  today,               today + timedelta(days=60)),
            ('FAMILY20',   'Скидка 20% на семейный размер XL',                   20, 'active',  today,               today + timedelta(days=45)),
            ('SUMMER15',   'Летняя скидка 15% (завершена)',                      15, 'archive', date(2024, 6, 1),    date(2024, 8, 31)),
            ('SPRING10',   'Весенняя скидка 10% (завершена)',                    10, 'archive', date(2024, 3, 1),    date(2024, 5, 31)),
            ('NY2024',     'Новогодняя скидка 30% 2024 (завершена)',             30, 'archive', date(2023, 12, 25),  date(2024, 1, 10)),
            ('LOYALTY5',   'Скидка 5% для постоянных клиентов (завершена)',       5, 'archive', date(2024, 1, 1),    date(2024, 3, 31)),
        ]
        for code, desc, disc, status, vf, vt in promo_data:
            PromoCode.objects.get_or_create(code=code, defaults={
                'description': desc, 'discount_percent': disc,
                'status': status, 'valid_from': vf, 'valid_to': vt,
            })
        self.stdout.write('Seeded main app data')

    def _seed_orders(self):
        from shop.models import Order, OrderItem, Pizza, PizzaSize, PizzaPrice, Courier
        from users.models import UserProfile
        from main.models import Review
        from django.contrib.auth.models import User

        buyer_usernames = ['ivan', 'anna', 'sergei', 'maria', 'dmitry', 'elena', 'alexei']
        statuses = ['new', 'preparing', 'delivering', 'delivered', 'delivered', 'delivered', 'cancelled']
        pizzas = list(Pizza.objects.filter(is_active=True))
        sizes = list(PizzaSize.objects.all())

        if not pizzas or not sizes:
            return

        couriers = list(Courier.objects.all())
        order_count = 0

        for i, uname in enumerate(buyer_usernames):
            try:
                profile = UserProfile.objects.get(user__username=uname)
            except UserProfile.DoesNotExist:
                continue

            # 1-2 orders per user so total >= 10
            for j in range(2):
                status = statuses[(i + j) % len(statuses)]
                courier = couriers[i % len(couriers)] if couriers and status == 'delivered' else None
                days_ago = (i * 5 + j * 2)
                created = timezone.now() - timedelta(days=days_ago)

                order = Order.objects.create(
                    client=profile,
                    status=status,
                    delivery_type='delivery' if j % 2 == 0 else 'pickup',
                    delivery_address=f'ул. Тестовая, {i+1}, кв. {j+1}' if j % 2 == 0 else '',
                    total_price=Decimal('0'),
                    courier=courier,
                )
                order.created_at = created
                order.save(update_fields=['created_at'])

                total = Decimal('0')
                for k in range(random.randint(1, 3)):
                    pizza = pizzas[(i + k) % len(pizzas)]
                    try:
                        pp = PizzaPrice.objects.filter(pizza=pizza).first()
                        if not pp:
                            continue
                        qty = random.randint(1, 2)
                        OrderItem.objects.create(
                            order=order, pizza=pizza,
                            size=pp.size, quantity=qty,
                            unit_price=pp.price,
                        )
                        total += pp.price * qty
                    except Exception:
                        pass

                order.total_price = total
                order.save(update_fields=['total_price'])
                order_count += 1

        self.stdout.write(f'Created {order_count} orders')

        # Add 10 reviews
        review_texts = [
            'Отличная пицца, доставили быстро!',
            'Очень вкусно, рекомендую Маргариту.',
            'Пепперони — лучшая! Буду заказывать снова.',
            'Хорошее качество, но доставка немного задержалась.',
            'Четыре сыра просто тает во рту. Превосходно!',
            'Приятные цены, большой выбор пицц. Доволен!',
            'Гавайская — необычно, но вкусно. Попробуйте!',
            'Вегетарианская понравилась даже моим детям.',
            'Быстрая доставка, упаковка не пострадала.',
            'Морская пицца — шедевр! Обязательно закажу ещё.',
        ]
        ratings = [5, 5, 4, 4, 5, 4, 3, 5, 4, 5]
        users = list(User.objects.filter(username__in=['ivan', 'anna', 'sergei', 'maria', 'dmitry',
                                                        'elena', 'alexei', 'courier1', 'courier2', 'admin']))
        for k, (text, rating) in enumerate(zip(review_texts, ratings)):
            user = users[k % len(users)] if users else None
            if user:
                Review.objects.get_or_create(
                    user=user,
                    text=text,
                    defaults={'rating': rating}
                )
        self.stdout.write('Created reviews')
