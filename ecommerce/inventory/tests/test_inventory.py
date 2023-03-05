import pytest
from django.utils import timezone
from ecommerce.inventory.models import Category

@pytest.mark.dbfixture
def category():
    return Category.objects.create(name='Test Category', slug='test-category', is_active=True)

def test_category_str(category):
    assert str(category) == 'Test Category'

def test_category_created_at(category):
    assert isinstance(category.created_at, timezone.datetime)

def test_category_updated_at(category):
    assert isinstance(category.updated_at, timezone.datetime)

def test_category_defaults():
    category = Category.objects.create(name='Test Category 2', slug='test-category-2')
    assert category.is_active == True
    assert category.parent == None

def test_category_parent(category):
    child_category = Category.objects.create(name='Child Category', slug='child-category', parent=category)
    assert child_category.parent == category
    assert child_category in category.children.all()

def test_category_slug_unique():
    Category.objects.create(name='Test Category 3', slug='test-category-3')
    with pytest.raises(Exception):
        Category.objects.create(name='Test Category 4', slug='test-category-3')