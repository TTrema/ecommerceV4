import decimal
import json
import random
import string
import xml.etree.ElementTree as ET

import requests
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from ecommerce.core.forms import CouponForm, PaymentForm, RefundForm, UserAddressForm, UserEditForm
from ecommerce.core.models import Address, Coupon, Order, OrderItem, Payment, Refund, UserProfile
from ecommerce.inventory.models import Brand, Category, Product
from decimal import Decimal

stripe.api_key = settings.STRIPESK


def create_ref_code():
    code = "".join(random.choices(string.ascii_lowercase + string.digits, k=20))
    while Order.objects.filter(ref_code=code).exists():
        code = "".join(random.choices(string.ascii_lowercase + string.digits, k=20))
    return code


def homepage(request):
    products = Product.objects.prefetch_related("product_image").filter(available=True)
    return render(request, "home.html", {"products": products})


def payment_success(request):
    return render(request, "user/payment_successful.html")


def paypaltoken(request):
    client_id = settings.PAYID
    client_secret = settings.PAYSK

    # Faça uma chamada à API de autenticação do PayPal para obter um token de acesso
    auth_url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    auth_data = {"grant_type": "client_credentials"}
    auth_headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    auth = requests.post(auth_url, data=auth_data, headers=auth_headers, auth=(client_id, client_secret))

    # Analise a resposta JSON e obtenha o token de acesso
    auth_json = auth.json()
    access_token = auth_json["access_token"]
    return access_token


def paypal(request):
    paypalid = settings.PAYPAL_ID
    order = Order.objects.get(user=request.user, ordered=False)
    if order.billing_address:

        session = request.session
        addresses = Address.objects.filter(user=request.user).order_by("-default")
        paypaltotal = str(order.get_total_frete()).replace(",", ".")
        accesse_token = paypaltoken(request)

        if "address" not in request.session:
            session["address"] = {"address_id": str(addresses[0].id)}
        else:
            session["address"]["address_id"] = str(addresses[0].id)
            session.modified = True

        context = {
            "accesse_token": accesse_token,
            "paypalid": paypalid,
            "addresses": addresses,
            "order": order,
            "paypaltotal": paypaltotal,
        }
        return render(request, "user/paypalpay.html", context)
    else:
        messages.warning(request, "Você ainda não adicionou nenhum endereço para a compra")
        return redirect("core:delivery_address")


@login_required
def edit_details(request):
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST)

        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)

    return render(request, "user/edit_details.html", {"user_form": user_form})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    product2 = Product.objects.filter(~Q(slug=slug) & Q(available=True))[:4]
    brand = product.brand
    if product.users_wishlist.filter(id=request.user.id).exists():
        wishlist = "Remover da lista de desejos"

    else:
        wishlist = "Adicionar a sua lista de desejos"
    return render(request, "product.html", {"product": product, "product2": product2, "brand": brand, "wishlist": wishlist})


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


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.filter(user=request.user, ordered=False).order_by("-start_date").first()
            context = {"object": order}
            return render(request, "user/order_summary.html", context)
        except Order.DoesNotExist:
            return render(request, "user/order_summary.html", {"message": "Você não tem nenhum item em seu carrinho"})


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
    addresses = Address.objects.filter(user=request.user).order_by("-default")
    return render(request, "user/addresses.html", {"addresses": addresses})


@login_required
def add_address(request):
    if request.method == "POST":
        checkout = request.GET.get("checkout")
        address_form = UserAddressForm(data=request.POST)
        if address_form.is_valid():
            address_form = address_form.save(commit=False)
            address_form.user = request.user
            address_form.save()
            if checkout == "checkout":
                next = "core:delivery_address"

            else:
                next = "core:addresses"

            if Address.objects.filter(user=request.user, default=True).exists():
                return HttpResponseRedirect(reverse(next))

            else:
                Address.objects.filter(user=request.user).update(default=True)
                return HttpResponseRedirect(reverse(next))

    else:
        address_form = UserAddressForm()
    return render(request, "user/edit_addresses.html", {"form": address_form})


@login_required
def edit_address(request, id):

    if request.method == "POST":
        checkout = request.GET.get("checkout")
        address = Address.objects.get(pk=id, user=request.user)
        address_form = UserAddressForm(instance=address, data=request.POST)
        if address_form.is_valid():
            address_form.save()
            if checkout == "checkout":
                return HttpResponseRedirect(reverse("core:delivery_address"))
            else:
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


@login_required
def wishlist(request):
    products = Product.objects.filter(users_wishlist=request.user)

    return render(request, "user/user_wish_list.html", {"wishlist": products})


@login_required
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    if product.users_wishlist.filter(id=request.user.id).exists():
        product.users_wishlist.remove(request.user)
        messages.success(request, "O produto " + product.name + " foi removido da sua lista de desejos")

    else:
        product.users_wishlist.add(request.user)
        messages.success(request, "O produto " + product.name + " foi adicionado a sua lista de desejos")

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def calculate_shipping(zip_code, shipping_method):
    # Define os parâmetros da requisição para o web service dos Correios
    if shipping_method == "S":
        shipping_method = "40010"
    else:
        shipping_method = "41106"

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
        "nCdServico": shipping_method,  # Código do serviço de entrega dos Correios (SEDEX)
        "nVlDiametro": 20,  # Diâmetro da encomenda (em centímetros)
        "StrRetorno": "xml",  # Tipo de retorno da requisição
    }

    # Faz a requisição para o web service dos Correios e recebe a resposta em XML
    response = requests.get(url, params=params)
    root = ET.fromstring(response.content)

    # Extrai o valor do frete e o prazo de entrega da resposta em XML
    price = root.find(".//Valor").text.replace(",", ".")
    price_decimal = decimal.Decimal(price).quantize(decimal.Decimal("0.01"))
    delivery_time = root.find(".//PrazoEntrega").text

    return (price_decimal, delivery_time)


@login_required
def delivery_address(request):

    if request.method == "POST":
        shipping_method = request.POST.get("shipping_method")
        shipping_type = get_object_or_404(Order, user=request.user, ordered=False)
        shipping_type.delivery_type = shipping_method
        shipping_type.save()

    session = request.session
    # if "purchase" not in request.session:
    #     messages.success(request, "Please select delivery option")
    #     return HttpResponseRedirect(request.META["HTTP_REFERER"])
    order = Order.objects.get(user=request.user, ordered=False)
    addresses = Address.objects.filter(user=request.user).order_by("-default")
    shipping_type = get_object_or_404(Order, user=request.user, ordered=False)

    try:
        default_address = Address.objects.get(user=request.user, default=True)
        shipping_cost = calculate_shipping(default_address.zip_code, shipping_type.delivery_type)

        order.delivery_price = shipping_cost[0]
        order.shipping_address = default_address
        order.save()
    except Address.DoesNotExist:
        shipping_cost = None  # ou fazer qualquer outra ação caso o objeto não exista

    # if "address" not in request.session:
    #     session["address"] = {"address_id": str(addresses[0].id)}
    # else:
    #     session["address"]["address_id"] = str(addresses[0].id)
    #     session.modified = True

    context = {
        "addresses": addresses,
        "couponform": CouponForm(),
        "order": order,
        "shipping_cost": shipping_cost,
        "shipping_type": shipping_type.delivery_type,
        "DISPLAY_COUPON_FORM": True,
    }
    return render(request, "user/delivery_address.html", context)


@login_required
def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        return None


@login_required
def delete_coupon(request):
    order = Order.objects.get(user=request.user)
    order.coupon = None
    order.save()

    return redirect("core:delivery_address")


@login_required
def delete_address(request, id):
    address = Address.objects.filter(pk=id, user=request.user).delete()
    return redirect("core:addresses")


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


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        ref_code_item = self.request.GET.get("ref_code")
        form = RefundForm(initial={"ref_code": ref_code_item} if ref_code_item else None)
        context = {"form": form, "ref_code_item": ref_code_item}
        return render(self.request, "user/request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get("ref_code")
            message = form.cleaned_data.get("message")
            email = form.cleaned_data.get("email")
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Recebemos o seu pedido de reembolso.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "Esse pedido não existe.")
                return redirect("core:request-refund")


def search(request):

    if "term" in request.GET:
        qs = Product.objects.filter(name__icontains=request.GET.get("term"))

        names = list()
        for product in qs:
            names.append(product.name)
        return JsonResponse(names, safe=False)

    q = request.GET["q"]
    products = Product.objects.filter(name__icontains=q)
    return render(request, "user/search_results.html", {"products": products})


@login_required
def user_orders(request):
    user_id = request.user.id
    orders = Order.objects.filter(user_id=user_id).filter(ordered=True)
    return render(request, "user/user_orders.html", {"orders": orders})


@csrf_exempt
def payment_complete(request):

    if request.method == "POST":
        order = Order.objects.get(user=request.user, ordered=False)
        orderID = request.POST.get("orderID")
        payerID = request.POST.get("payerID")
        amount = request.POST.get("amount")

        decimal_amount = Decimal(amount)

        if decimal_amount == order.get_total_frete():

            # Processar o pagamento
            payment = Payment()
            payment.charge_id = orderID
            payment.user = request.user
            payment.amount = order.get_total_frete()
            payment.save()

            # Atualizar o pedido
            order.ordered = True
            order.payment_option = "P"
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            # Atualizar os itens do pedido
            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            # Redirecionar para a página de sucesso de pagamento
            return redirect(reverse("core:payment_success"))

        else:
            # O valor do pagamento não corresponde ao total da compra
            return render(request, "payment_error.html", {"error_message": "O valor do pagamento não corresponde ao total da compra."})

    else:
        # A solicitação não é do tipo POST
        return render(request, "payment_error.html", {"error_message": "A solicitação não é do tipo POST."})


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {"order": order, "DISPLAY_COUPON_FORM": False, "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY}
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(userprofile.stripe_customer_id, limit=3, object="card")
                card_list = cards["data"]
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({"card": card_list[0]})
            return render(self.request, "user/payment.html", context)
        else:
            messages.warning(self.request, "Você ainda não adicionou nenhum endereço para a compra")
            return redirect("core:delivery_address")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get("stripeToken")
            save = form.cleaned_data.get("save")
            use_default = form.cleaned_data.get("use_default")

            if save:
                if userprofile.stripe_customer_id != "" and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(userprofile.stripe_customer_id)

                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer["id"]
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(amount=amount, currency="usd", customer=userprofile.stripe_customer_id)  # cents
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(amount=amount, currency="usd", source=token)  # cents

                # create the payment
                payment = Payment()
                payment.charge_id = charge["id"]
                payment.user = self.request.user
                payment.amount = order.get_total_frete()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.payment_option = "S"
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "Your order was successful!")
                return redirect("core:payment_success")

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get("error", {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API

                messages.warning(self.request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(self.request, "A serious error occurred. We have been notifed.")
                return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")
