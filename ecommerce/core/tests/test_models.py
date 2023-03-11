from decimal import Decimal

import pytest

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from ecommerce.inventory.models import Product, Brand, Category
from ecommerce.core.models import Address, Order, OrderItem


class Item:
    def __init__(self, name, price):
        self.name = name
        self.price = price


@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create_user(
        email='testuser@example.com',
        password='testpass',
        username='Test User',
        cpf='12345678901',
        
    )


@pytest.fixture
def brands():
    brand1 = Brand.objects.create(title="Brand 1")
    return [brand1]

@pytest.fixture
def categories():
    category1 = Category.objects.create(name="Category 1")
    return [category1]

@pytest.fixture
def product(brands, categories):
    return Product.objects.create(
        name = "Essential Goethe",
        slug = "essential-goethe",
        brand = brands[0],
        category = categories[0],
        description = "Essential Goethe: Livro que contém algumas das obras mais importantes do escritor alemão Johann Wolfgang von Goethe. Preço original de R$ 70,00 e preço de desconto de R$ 50,00.",
        price = "70.00",
        discount_price = "50.00",
        available = True,
        created_at = "2023-03-10T21:12:47.269Z",
        updated_at = "2023-03-10T21:23:04.630Z",
    )


@pytest.fixture
def address(user):
    return Address.objects.create(
        user=user,
        full_name='Test User',
        zip_code='12345678',
        city='Test City',
        state='Test State',
        bairro='Test Bairro',
        street='Test Street',
        number=123,
        complemento='Test Complemento',
        phone='(11) 98765-4321',
        referencia='Test Referencia',
        default=True,
    )


@pytest.fixture
def order(user, product):
    item = OrderItem.objects.create(
        user=user,
        product=product,
        quantity=1,
        ordered=False,
    )

    return Order.objects.create(
        user=user,
        ref_code='ABCD1234',
        start_date=timezone.now(),
        ordered_date=timezone.now(),
        delivery_type='P',
        delivery_price=Decimal('10'),
        payment_option='P',
        ordered=False,
    )

@pytest.mark.django_db
def test_create_user():
    User = get_user_model()
    user = User.objects.create_user(
        email='testuser2@example.com',
        password='testpass',
        username='Test User 2',
        cpf='12345678901',
    )

    assert user.email == 'testuser2@example.com'
    assert user.username == 'Test User 2'
    assert user.cpf == '12345678901'
    assert str(user) == 'testuser2@example.com'

@pytest.mark.django_db
def test_create_user_without_email():
    User = get_user_model()

    with pytest.raises(ValueError):
        User.objects.create_user(
            email='',
            password='testpass',
            username='Test User 2',
            cpf='12345678901',
        )

@pytest.mark.django_db
def test_create_superuser():
    User = get_user_model()
    admin_user = User.objects.create_superuser(
        email='admin@example.com',
        password='testpass',
        username='Admin User',
        cpf='12345678901',
    )

    assert admin_user.is_superuser
    assert admin_user.is_staff
    assert str(admin_user) == 'admin@example.com'

@pytest.mark.django_db
def test_order_str(order):
    assert str(order) == 'testuser@example.com'

@pytest.mark.django_db
def test_order_save_without_billing_address(order):
    order.shipping_address = Address.objects.create(
        user=order.user,
        full_name='Test User',
        zip_code='12345-678',
        city='Test City',
        state='Test State',
        bairro='Test Bairro',
        street='Test Street',
        number=123,
        complemento='Test Complemento',
        phone='11987654321',
        referencia='Test Referencia',
        default=True,
    )

    order.save()

    assert order.billing_address == order.shipping_address