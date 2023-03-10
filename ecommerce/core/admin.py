from django.contrib import admin
from django.contrib.auth import get_user_model

from ecommerce.core.models import (Address, Coupon, Order, OrderItem, Payment,
                                   User, UserProfile)

User = get_user_model()


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = "Update orders to refund granted"


class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "username", "is_staff"]


class OrderAdmin(admin.ModelAdmin):

    list_display = ["user", "ordered", "refund_requested", "refund_granted", "shipping_address", "billing_address", "payment", "coupon"]
    list_display_links = ["user", "shipping_address", "billing_address", "payment", "coupon"]
    list_filter = ["ordered", "refund_requested", "refund_granted"]
    search_fields = ["user__email", "ref_code"]
    actions = [make_refund_accepted]


class AddressInline(admin.StackedInline):
    model = Address
    extra = 3


class UserAdmin(admin.ModelAdmin):
    inlines = [AddressInline]


class OrderInline(admin.StackedInline):
    model = Order
    extra = 0


class PaymentAdmin(admin.ModelAdmin):
    inlines = [OrderInline]


admin.site.register(User, UserAdmin)
admin.site.register(Coupon)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(UserProfile)
