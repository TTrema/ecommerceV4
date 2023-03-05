from django.contrib import admin
from ecommerce.inventory.models import Category, Product, ProductImage, Brand

admin.site.register(Category)
admin.site.register(Brand)


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    extra = 3

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

admin.site.register(Product, ProductAdmin)