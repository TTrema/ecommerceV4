from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Category, Brand, Product, ProductImage

class CategoryListView(ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'category_detail.html'
    context_object_name = 'category'

class BrandListView(ListView):
    model = Brand
    template_name = 'brand_list.html'
    context_object_name = 'brands'

class BrandDetailView(DetailView):
    model = Brand
    template_name = 'brand_detail.html'
    context_object_name = 'brand'

class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get_object(self):
        return get_object_or_404(Product, slug=self.kwargs.get('slug'))

class ProductImageView(DetailView):
    model = ProductImage
    template_name = 'product_image.html'
    context_object_name = 'product_image'

    def get_object(self):
        return get_object_or_404(ProductImage, pk=self.kwargs.get('pk'))