from django.urls import path
from .views import homepage, product_detail, category_list, brand_list, ProductDetailView


app_name = 'core'

urlpatterns = [
    path('', homepage, name='store_home'),
    path('produto/<slug:slug>/', product_detail, name='product_detail'), 
    path('categorias/<slug:category_slug>/', category_list, name='category_list'), 
    path('marcas/<slug:brand_slug>/', brand_list, name='brand_list'), 
    # path('produto/<slug>/', ProductDetailView, name='product_detail'),
    # path('', HomeView.as_view(), name='home'),
    # path('<slug:slug>/', views.product_detail, name='product_detail'),
    # path('shop/<slug:category_slug>/', views.category_list, name='category_list'),

]
