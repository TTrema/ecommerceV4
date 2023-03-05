from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView, View
from django.db.models import Q

from ecommerce.inventory.models import Product, Category, Brand

def homepage(request):
    products = Product.objects.prefetch_related("product_image").filter(available=True)
    return render(request, "home.html", {"products": products})

# class HomeView(ListView):
#     model = Product
#     paginate_by = 10brand_list
#     template_name = "home.html"

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    product2 = Product.objects.filter(~Q(slug=slug) & Q(available=True))[:4]
    brand = product.brand # acessa o objeto Brand relacionado ao objeto Product
    return render(request, "product.html", {"product": product, "product2": product2, "brand": brand})

class ProductDetailView(DetailView):
    model = Product
    template_name = "product.html"


def get_descendants(category):
    descendants = category.children.all()
    for child in descendants:
        descendants = descendants | get_descendants(child)
    return descendants

def category_list(request, category_slug=None):
    category = get_object_or_404(Category, slug=category_slug)
    descendants = get_descendants(category)
    products = Product.objects.filter(category__in=descendants | Category.objects.filter(id=category.id))
    return render(request, "category.html", {"category": category, "products": products})

def brand_list(request, brand_slug=None):
    brand = get_object_or_404(Brand, slug=brand_slug)
    products = Product.objects.filter(brand=brand)
    return render(request, "brand.html", {"brand": brand, "products": products})
