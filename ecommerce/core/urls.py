from django.urls import path
from .views import (
    homepage,
    product_detail,
    category_list,
    brand_list,
    OrderSummaryView,
    add_to_cart,
    remove_single_item_from_cart,
    remove_from_cart,
    view_address,
    add_address,
    edit_address,
    delete_address,
    set_default,
    delivery_address,
    AddCouponView,
    calculate_shipping,
    search,

)


app_name = "core"

urlpatterns = [
    path("", homepage, name="store_home"),
    path("produto/<slug:slug>/", product_detail, name="product_detail"),
    path("categorias/<slug:category_slug>/", category_list, name="category_list"),
    path("marcas/<slug:brand_slug>/", brand_list, name="brand_list"),
    path("add-to-cart/<slug>/", add_to_cart, name="add-to-cart"),
    path("order-summary/", OrderSummaryView.as_view(), name="order-summary"),
    path("remove-from-cart/<slug>/", remove_from_cart, name="remove-from-cart"),
    path("remove-item-from-cart/<slug>/", remove_single_item_from_cart, name="remove-single-item-from-cart"),
    path("enderecos/", view_address, name="addresses"),
    path("adicionar-endereco/", add_address, name="add_address"),
    path("endereco/editar/<slug:id>/", edit_address, name="edit_address"),
    path("endereco/deletar/<slug:id>/", delete_address, name="delete_address"),
    path("enderecos/set_default/<slug:id>/", set_default, name="set_default"),
    path("endereco-de-entrega/", delivery_address, name="delivery_address"),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('frete/', calculate_shipping, name='calculate_shipping'),
    path('pesquisa/', search, name='product_search'),



]


