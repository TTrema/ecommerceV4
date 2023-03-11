import pytest
from django.core.management import call_command
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client

from ecommerce.inventory.models import Brand, Category, Product, ProductImage


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        # Load the fixtures
        call_command('loaddata', 'db_brand_fixture.json')
        call_command('loaddata', 'db_category_fixture.json')
        call_command('loaddata', 'db_product_fixture.json')
        call_command('loaddata', 'db_image_fixture.json')


@pytest.fixture
def brand():
    return Brand.objects.first()


@pytest.fixture
def category():
    return Category.objects.first()


@pytest.fixture
def product():
    return Product.objects.first()


@pytest.mark.django_db
def test_brand_str_method(brand):
    assert str(brand) == brand.title


@pytest.mark.django_db
def test_brand_get_absolute_url_method(brand):
    assert brand.get_absolute_url() == reverse('core:brand_list', args=[brand.slug])


@pytest.mark.django_db
def test_category_str_method(category):
    assert str(category) == category.name


@pytest.mark.django_db
def test_category_get_absolute_url_method(category):
    assert category.get_absolute_url() == reverse('core:category_list', args=[category.slug])


@pytest.mark.django_db
def test_product_str_method(product):
    assert str(product) == product.name


@pytest.mark.django_db
def test_product_get_absolute_url_method(product):
    assert product.get_absolute_url() == reverse('core:product_detail', args=[product.slug])


@pytest.mark.django_db
def test_product_offprice_method(product):
    assert product.offprice() == str(round((1 - product.discount_price / product.price) * 100))



@pytest.mark.django_db
def test_product_get_add_to_cart_url_method(product):
    assert product.get_add_to_cart_url() == reverse('core:add-to-cart', kwargs={'slug': product.slug})


@pytest.mark.django_db
def test_product_get_remove_from_cart_url_method(product):
    assert product.get_remove_from_cart_url() == reverse('core:remove-from-cart', kwargs={'slug': product.slug})


@pytest.fixture
def image_file():
    return SimpleUploadedFile(
        "image.jpg",
        b"this is a test image",
        content_type="image/jpeg"
    )


@pytest.fixture
def product_image(product, image_file):
    return ProductImage.objects.create(product=product, image=image_file, is_feature=False)


User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(email='testuser@test.com', password='testpass')

@pytest.mark.django_db
def test_product_users_wishlist_method(product, user):
    assert not product.users_wishlist.filter(id=user.id).exists()
    product.users_wishlist.add(user)
    assert product.users_wishlist.filter(id=user.id).exists()
    product.users_wishlist.remove(user)
    assert not product.users_wishlist.filter(id=user.id).exists()