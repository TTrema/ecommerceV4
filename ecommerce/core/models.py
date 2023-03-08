from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from ecommerce.inventory.models import Product


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O Email deve ser fornecido.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, blank=True, null=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    objects = UserManager()

    def __str__(self):
        return self.email


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    number = models.IntegerField()
    complemento = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=11)
    referencia = models.CharField(max_length=255, blank=True, null=True)
    default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.street


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_item_price(self):
        return self.quantity * self.product.price

    def get_total_discount_item_price(self):
        return self.quantity * self.product.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.product.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    coupon = models.ForeignKey("Coupon", on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(Address, related_name="billing_address", on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey(Address, related_name="shipping_address", on_delete=models.SET_NULL, blank=True, null=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

    def get_absolute_url(self):
        return reverse("order-summary")


class Coupon(models.Model):
    code = models.CharField(max_length=6)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.code