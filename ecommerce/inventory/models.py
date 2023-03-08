from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "categories"

    def get_absolute_url(self):
        return reverse("core:category_list", args=[self.slug])        

    def __str__(self):
        return self.name

class Brand(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("core:brand_list", args=[self.slug])        

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "products"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("core:product_detail", args=[self.slug])

    def offprice(self):
        return str(int((1 - self.discount_price / self.price) * 100))
    
    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_image')
    image = models.ImageField(upload_to='product_images')
    is_feature = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"



# class Order(models.Model):
#     STATUS_CHOICES = (
#         ('pending', 'Pending'),
#         ('processing', 'Processing'),
#         ('shipped', 'Shipped'),
#         ('delivered', 'Delivered'),
#         ('cancelled', 'Cancelled'),
#     )

#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
#     order_date = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
#     total = models.DecimalField(max_digits=10, decimal_places=2)

#     class Meta:
#         verbose_name_plural = "orders"

#     def __str__(self):
#         return str(self.id)


# class Wishlist(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     products = models.ManyToManyField(Product)

# class Review(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     title = models.CharField(max_length=100)
#     content = models.TextField()
#     rating = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)