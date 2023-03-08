import xml.etree.ElementTree as ET
from django.http import JsonResponse
from django.views.decorators.http import require_GET

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView, View

from ecommerce.core.forms import CouponForm, UserAddressForm
from ecommerce.core.models import Address, Coupon, Order, OrderItem
from ecommerce.inventory.models import Brand, Category, Product


def homepage(request):
    products = Product.objects.prefetch_related("product_image").filter(available=True)
    return render(request, "home.html", {"products": products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    product2 = Product.objects.filter(~Q(slug=slug) & Q(available=True))[:4]
    brand = product.brand  # acessa o objeto Brand relacionado ao objeto Product
    return render(request, "product.html", {"product": product, "product2": product2, "brand": brand})


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


class AddToCartView(LoginRequiredMixin, View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        order_item, created = OrderItem.objects.get_or_create(product=product, user=request.user, ordered=False)
        order_qs = Order.objects.filter(user=request.user, ordered=False)

        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(product__slug=product.slug).exists():
                order_item.quantity += 1
                order_item.save()
                return redirect("core:order-summary")
            else:
                order.items.add(order_item)
                return redirect("core:order-summary")
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(user=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            return redirect("core:order-summary")


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            context = {"object": order}
            return render(request, "user/order_summary.html", context)
        except Order.DoesNotExist:
            return render(request, "user/order_summary.html", {"message": "Você não tem nenhum item em seu carrinho"})


# @login_required
# def order_summary(request):
#     order_items = OrderItem.objects.filter(user=request.user, ordered=False)
#     context = {"order_items": order_items}
#     return render(request, "user/order_summary.html", context)


@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(product=product, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product__slug=product.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "A quantidade do Produto foi ajustada")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "O produto foi adicionado a seu carrinho.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "O produto foi adicionado ao seu carrinho.")
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product__slug=product.slug).exists():
            order_item = OrderItem.objects.filter(product=product, user=request.user, ordered=False)[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "O produto foi removido do seu carrinho")
            return redirect("core:order-summary")
        else:
            messages.info(request, "O produto não estava no seu carrinho")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "Você não tem um pedido")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product__slug=product.slug).exists():
            order_item = OrderItem.objects.filter(product=product, user=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "A quantidade do Produto foi ajustada.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "O produto não estava no seu carrinho")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "Você não tem um pedido")
        return redirect("core:product", slug=slug)


@login_required
def view_address(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, "user/addresses.html", {"addresses": addresses})


@login_required
def add_address(request):
    if request.method == "POST":
        address_form = UserAddressForm(data=request.POST)
        if address_form.is_valid():
            address_form = address_form.save(commit=False)
            address_form.user = request.user
            address_form.save()
            return HttpResponseRedirect(reverse("core:addresses"))
        else:
            return HttpResponse("Error handler content", status=400)
    else:
        address_form = UserAddressForm()
    return render(request, "user/edit_addresses.html", {"form": address_form})


@login_required
def edit_address(request, id):
    if request.method == "POST":
        address = Address.objects.get(pk=id, user=request.user)
        address_form = UserAddressForm(instance=address, data=request.POST)
        if address_form.is_valid():
            address_form.save()
            return HttpResponseRedirect(reverse("core:addresses"))
    else:
        address = Address.objects.get(pk=id, user=request.user)
        address_form = UserAddressForm(instance=address)
    return render(request, "user/edit_addresses.html", {"form": address_form})


@login_required
def delete_address(request, id):
    address = Address.objects.filter(pk=id, user=request.user).delete()
    return redirect("core:addresses")


@login_required
def set_default(request, id):
    Address.objects.filter(user=request.user, default=True).update(default=False)
    Address.objects.filter(pk=id, user=request.user).update(default=True)

    previous_url = request.META.get("HTTP_REFERER")

    if "endereco-de-entrega" in previous_url:
        return redirect("core:delivery_address")

    return redirect("core:addresses")


def calculate_shipping(zip_code):
    # Define os parâmetros da requisição para o web service dos Correios
    url = "http://ws.correios.com.br/calculador/CalcPrecoPrazo.aspx"
    params = {
        "nCdEmpresa": "",
        "sDsSenha": "",
        "sCepOrigem": "05877-180",  # CEP da origem (exemplo: São Paulo/SP)
        "sCepDestino": zip_code,  # CEP do destino (informado pelo usuário)
        "nVlPeso": 20,  # Peso do pacote (em quilogramas, informado pelo usuário)
        "nCdFormato": 1,  # Formato da encomenda (caixa/pacote)
        "nVlComprimento": 20,  # Comprimento da encomenda (em centímetros)
        "nVlAltura": 20,  # Altura da encomenda (em centímetros)
        "nVlLargura": 20,  # Largura da encomenda (em centímetros)
        "nVlDiametro": 0,  # Diâmetro da encomenda (em centímetros)
        "sCdMaoPropria": "N",  # Indica se a encomenda será entregue com o serviço "Mão própria"
        "nVlValorDeclarado": 50,  # Valor declarado da encomenda (em reais)
        "sCdAvisoRecebimento": "N",  # Indica se a encomenda será entregue com o serviço "Aviso de recebimento"
        "nCdServico": "41106",  # Código do serviço de entrega dos Correios (SEDEX)
        "nVlDiametro": 20,  # Diâmetro da encomenda (em centímetros)
        "StrRetorno": "xml",  # Tipo de retorno da requisição
    }

    # Faz a requisição para o web service dos Correios e recebe a resposta em XML
    response = requests.get(url, params=params)
    root = ET.fromstring(response.content)

    # Extrai o valor do frete e o prazo de entrega da resposta em XML
    price = float(root.find(".//Valor").text.replace(",", "."))
    delivery_time = root.find(".//PrazoEntrega").text
    return (price, delivery_time)


@login_required
def delivery_address(request):

    session = request.session
    # if "purchase" not in request.session:
    #     messages.success(request, "Please select delivery option")
    #     return HttpResponseRedirect(request.META["HTTP_REFERER"])
    order = Order.objects.get(user=request.user, ordered=False)
    addresses = Address.objects.filter(user=request.user).order_by("-default")
    frete = get_object_or_404(Address, default=True)
    shipping_cost = calculate_shipping(frete.zip_code)  # Exemplo de cálculo de frete

    if "address" not in request.session:
        session["address"] = {"address_id": str(addresses[0].id)}
    else:
        session["address"]["address_id"] = str(addresses[0].id)
        session.modified = True

    context = {"addresses": addresses, "couponform": CouponForm(), "order": order, "shipping_cost": shipping_cost, "DISPLAY_COUPON_FORM": True}
    return render(request, "user/delivery_address.html", context)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        return None


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            code = form.cleaned_data.get("code")
            order = Order.objects.filter(user=self.request.user, ordered=False).first()
            coupon = get_coupon(self.request, code)
            if coupon:
                order.coupon = coupon
                order.save()
                messages.success(self.request, "Cupom Adicionado com sucesso")
            else:
                messages.info(self.request, "O cupom é invalido")
            return redirect("core:delivery_address")
        else:
            messages.info(self.request, "O cupom é invalido")
            return redirect("core:delivery_address")


from django.db.models import Q
from django.views.generic import ListView

def search(request):

    if 'term' in request.GET:
        qs = Product.objects.filter(name__icontains=request.GET.get('term'))
        print(qs)
        names = list()
        for product in qs:
            names.append(product.name)
        return JsonResponse(names, safe=False)    
    
    q=request.GET['q']
    products = Product.objects.filter(name__icontains=q)
    return render(request, "search_results.html", {"products": products})


