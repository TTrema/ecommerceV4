from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.utils.translation import gettext_lazy as _

from ecommerce.core.extra.cpfvalidation import (CPFValidationMixin,
                                                CPFValidationMixin2)
from ecommerce.core.models import Address, User

User = get_user_model()


class RegistrationForm(CPFValidationMixin, UserCreationForm):

    username = forms.CharField(label="Enter Username", min_length=4, max_length=50, help_text="Required")
    email = forms.EmailField(max_length=100, help_text="Required", error_messages={"required": "Sorry, you will need an email"})
    cpf = forms.CharField(
        max_length=11,
        help_text="Required",
        required=True,
    )

    class Meta:
        model = User
        fields = ("email", "username", "cpf", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já se encontra cadastrado, Por Favor, use outro E-mail")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control mb-3", "placeholder": "Nome Completo"})
        self.fields["email"].widget.attrs.update({"class": "form-control mb-3", "placeholder": "E-mail", "name": "email", "id": "id_email"})
        self.fields["cpf"].widget.attrs.update({"class": "form-control mb-3", "placeholder": "CPF", "name": "cpf", "id": "id_cpf"})
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control mb-3", "placeholder": "Senha", "name": "password1", "id": "id_password1"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control mb-3", "placeholder": "Digite a senha novamente", "name": "password2", "id": "id_password2"}
        )

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["username"]
        user.cpf = self.cleaned_data["cpf"]
        if commit:
            user.save()
        return user


class UserEditForm(CPFValidationMixin2, forms.ModelForm):

    email = forms.EmailField(
        label="Account email (can not be changed)",
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control mb-3", "placeholder": "email", "id": "form-email", "readonly": "readonly"}),
    )

    username = forms.CharField(
        label="Nome Completo",
        min_length=4,
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control mb-3", "placeholder": "Nome Completo", "id": "form-user_name"}),
    )

    cpf = forms.CharField(
        label="CPF",
        min_length=11,
        max_length=11,
        widget=forms.TextInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "CPF",
                "id": "cpf",
            }
        ),
    )

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "cpf",
        )
        labels = {
            "email": "email",
            "username": "user_name",
            "cpf": "CPF",
        }


class CouponForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Promo code", "aria-label": "Recipient's username", "aria-describedby": "basic-addon2"}
        ),
    )


class RefundForm(forms.Form):
    ref_code = forms.CharField(label='Código do pedido:')
    message = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), label='Mensagem:')
    email = forms.EmailField()


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)


class UserAddressForm(forms.ModelForm):
    zip_code = forms.CharField(
        label="CEP",
        widget=forms.TextInput(attrs={"class": "form-control mb-2 account-form col-md-2", "placeholder": "CEP", "id": "id_zip_code"}),
        max_length=8,
    )
    phone = forms.CharField(
        label="Telefone",
        widget=forms.TextInput(attrs={"class": "form-control mb-2 account-form col-md-2", "placeholder": "Telefone", "id": "id_phone"}),
        validators=[
            MinLengthValidator(10, message="O telefone deve ter pelo menos 10 caracteres."),
            MaxLengthValidator(11, message="O telefone deve ter no máximo 11 caracteres."),
        ],
        max_length=11,
    )

    class Meta:
        model = Address
        fields = ["full_name", "zip_code", "city", "state", "bairro", "street", "number", "complemento", "phone", "referencia"]
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
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control mb-2 account-form col-md-4", "placeholder": "Nome", "id": "id_full_name"}),
            "city": forms.TextInput(
                attrs={"class": "form-control mb-2 account-form col-md-6", "placeholder": "Cidade", "id": "id_city", "readonly": "readonly"}
            ),
            "state": forms.TextInput(
                attrs={"class": "form-control mb-2 account-form col-md-6", "placeholder": "Estado", "id": "id_state", "readonly": "readonly"}
            ),
            "bairro": forms.TextInput(
                attrs={
                    "class": "form-control mb-2 account-form col-md-2",
                    "placeholder": "Bairro",
                    "id": "id_bairro",
                }
            ),
            "street": forms.TextInput(attrs={"class": "form-control mb-2 account-form col-md-6", "placeholder": "Rua", "id": "id_street"}),
            "number": forms.TextInput(
                attrs={"class": "form-control mb-2 account-form col-md-6", "placeholder": "Numero", "id": "id_number", "max_length": "3"}
            ),
            "complemento": forms.TextInput(
                attrs={"class": "form-control mb-2 account-form col-md-9", "placeholder": "Complemento", "id": "id_complemento"}
            ),
            "referencia": forms.TextInput(
                attrs={"class": "form-control mb-2 account-form col-md-9", "placeholder": "Referencia", "id": "id_referencia"}
            ),
        }

    def clean_zip_code(self):
        zip_code = str(self.cleaned_data.get("zip_code"))
        if not zip_code.isdigit():
            raise forms.ValidationError("O CEP deve conter apenas números.")
        return zip_code

    def clean_number(self):
        number = str(self.cleaned_data.get("number"))
        if not number.isdigit():
            raise forms.ValidationError("O número deve conter apenas números.")
        return number

    def clean_phone(self):
        phone = str(self.cleaned_data.get("phone"))
        if not phone.isdigit():
            raise forms.ValidationError("O telefone deve conter apenas números.")
        return phone
