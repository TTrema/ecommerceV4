from django.contrib import admin
from ecommerce.core.models import User, Address, Coupon
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'is_staff']


class AddressInline(admin.StackedInline):
    model = Address
    extra = 3

class UserAdmin(admin.ModelAdmin):
    inlines = [AddressInline]

admin.site.register(User, UserAdmin)
admin.site.register(Coupon)