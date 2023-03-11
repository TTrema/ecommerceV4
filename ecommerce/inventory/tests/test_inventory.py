from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed
from ecommerce.inventory.models import Brand, Category, Product, ProductImage
from django.core.files.uploadedfile import SimpleUploadedFile
import pytest

# test Category model
@pytest.mark.django_db
def test_category_model():
    category = Category.objects.create(name="Test Category", slug="test-category")
    assert category.name == "Test Category"
    assert category.slug == "test-category"
    assert str(category) == "Test Category"
    assert category.get_absolute_url() == reverse("core:category_list", args=["test-category"])

# test Brand model
@pytest.mark.django_db
def test_brand_model():
    brand = Brand.objects.create(title="Test Brand", slug="test-brand")
    assert brand.title == "Test Brand"
    assert brand.slug == "test-brand"
    assert str(brand) == "Test Brand"
    assert brand.get_absolute_url() == reverse("core:brand_list", args=["test-brand"])

# test Product model
@pytest.mark.django_db
def test_product_model():
    brand = Brand.objects.create(title="Test Brand", slug="test-brand")
    category = Category.objects.create(name="Test Category", slug="test-category")
    product = Product.objects.create(
        name="Test Product",
        slug="test-product",
        brand=brand,
        category=category,
        description="This is a test product",
        price=10.0,
        discount_price=8.0,
        available=True,
    )
    assert product.name == "Test Product"
    assert product.slug == "test-product"
    assert product.brand == brand
    assert product.category == category
    assert product.description == "This is a test product"
    assert product.price == 10.0
    assert product.discount_price == 8.0
    assert product.available == True
    assert str(product) == "Test Product"
    assert product.offprice() == "20"
    assert product.get_absolute_url() == reverse("core:product_detail", args=["test-product"])
    assert product.get_add_to_cart_url() == reverse("core:add-to-cart", kwargs={"slug": "test-product"})
    assert product.get_remove_from_cart_url() == reverse("core:remove-from-cart", kwargs={"slug": "test-product"})
