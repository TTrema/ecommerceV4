from django import forms
from ecommerce.core.models import Address
from pycep_correios import get_address_from_cep
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db.models import Q
from django.utils.html import escape
from ecommerce.inventory.models import Product

class ProductSearchForm(forms.Form):
    search = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['search'].widget.attrs.update({'autocomplete': 'off'})

    def clean_search(self):
        search = self.cleaned_data['search']
        if len(search.strip()) < 2:
            raise forms.ValidationError("Search term must be at least 2 characters long.")
        return search

    def get_autocomplete(self):
        query = self.cleaned_data.get('search', '')
        results = []
        if query:
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = Product.objects.filter(queries)
            for product in products:
                results.append({'label': product.name, 'value': escape(product.name)})
        return results




class CouponForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Promo code", "aria-label": "Recipient's username", "aria-describedby": "basic-addon2"}
        )
    )


class UserAddressForm(forms.ModelForm):
    zip_code = forms.CharField(label="CEP", widget=forms.TextInput(attrs={"class": "form-control mb-2 account-form col-md-2", "placeholder": "CEP", "id": "id_zip_code"}), max_length=8,)
    phone = forms.CharField(
    label="Telefone",
    widget=forms.TextInput(attrs={"class": "form-control mb-2 account-form col-md-2", "placeholder": "Telefone", "id": "id_phone"}),
    validators=[
            MinLengthValidator(10, message="O telefone deve ter pelo menos 10 caracteres."),
            MaxLengthValidator(11, message="O telefone deve ter no máximo 11 caracteres.")
        ],
    max_length=11,
)
    
    class Meta:
        model = Address
        fields = ["full_name", "zip_code", "city", "state", "bairro", "street", "number", "complemento", "phone", "referencia", "default"]
        labels = {
            "full_name": "Nome",
            "city": "Cidade",
            "state": "Estado",
            "bairro": "Bairro",
            "street": "Rua",
            "number": "Numero",
            "complemento": "Complemento",
            "phone": "Telefone",
            "referencia": "Referencia",
            "default": "Principal"
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control mb-2 account-form col-md-4", "placeholder": "Nome", "id": "id_full_name"}),
            "city": forms.TextInput(attrs={"class": "form-control mb-2 account-form col-md-6", "placeholder": "Cidade", "id": "id_city", 'readonly': 'readonly'}),
            "state": forms.TextInput(attrs={"class": "form-control mb-2 account-form col-md-6", "placeholder": "Estado", "id": "id_state", 'readonly': 'readonly'}),
            "bairro": forms.TextInput(attrs={"class": "form-control mb-2 account-form col-md-2", "placeholder": "Bairro", "id": "id_bairro",}),
            "street": forms.TextInput(attrs={"class": "form-control mb-2 account-form col-md-6", "placeholder": "Rua", "id": "id_street"}),
            "number": forms.TextInput(attrs={"class": "form-control mb-2 account-form col-md-6", "placeholder": "Numero", "id": "id_number", "max_length": "3"}),
            "complemento": forms.TextInput(attrs={"class": "form-control mb-2 account-form col-md-9", "placeholder": "Complemento", "id": "id_complemento"}),
            
            "referencia": forms.TextInput(attrs={"class": "form-control mb-2 account-form col-md-9", "placeholder": "Referencia", "id": "id_referencia"}),
            "default": forms.CheckboxInput(attrs={"class": "form-check-input", "placeholder": "Principal", "id": "id_default"}),
        }

    def clean_zip_code(self):
        zip_code = str(self.cleaned_data.get('zip_code'))
        if not zip_code.isdigit():
            raise forms.ValidationError("O CEP deve conter apenas números.")
        return zip_code

    def clean_number(self):
        number = str(self.cleaned_data.get('number'))
        if not number.isdigit():
            raise forms.ValidationError("O número deve conter apenas números.")
        return number

    def clean_phone(self):
        phone = str(self.cleaned_data.get('phone'))
        if not phone.isdigit():
            raise forms.ValidationError("O telefone deve conter apenas números.")
        return phone
