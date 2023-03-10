from django import forms

from ecommerce.core.models import User


class CPFValidationMixin:
    def clean_cpf(self):
        cpf = self.cleaned_data["cpf"]
        cpf = cpf.replace(".", "").replace("-", "")  # remover pontos e traços do CPF
        if User.objects.filter(cpf=cpf).exists():
            raise forms.ValidationError("Este CPF já se encontra cadastrado, Por Favor, use outro CPF")
        if not cpf.isdigit():  # verificar se o CPF contém apenas dígitos
            raise forms.ValidationError("CPF inválido")

        # Verificar se o CPF tem 11 dígitos
        if len(cpf) != 11:
            raise forms.ValidationError("CPF inválido")

        # Verificar se todos os dígitos do CPF são iguais (ex: 111.111.111-11)
        if len(set(cpf)) == 1:
            raise forms.ValidationError("CPF inválido")

        # Calcular o primeiro dígito verificador do CPF
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito1 = (soma * 10) % 11
        if digito1 == 10:
            digito1 = 0

        # Verificar se o primeiro dígito verificador está correto
        if digito1 != int(cpf[9]):
            raise forms.ValidationError("CPF inválido")

        # Calcular o segundo dígito verificador do CPF
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito2 = (soma * 10) % 11
        if digito2 == 10:
            digito2 = 0

        # Verificar se o segundo dígito verificador está correto
        if digito2 != int(cpf[10]):
            raise forms.ValidationError("CPF inválido")

        return cpf


class CPFValidationMixin2:
    def clean_cpf(self):
        cpf = self.cleaned_data["cpf"]
        cpf = cpf.replace(".", "").replace("-", "")  # remover pontos e traços do CPF
        if not cpf.isdigit():  # verificar se o CPF contém apenas dígitos
            raise forms.ValidationError("CPF inválido")

        # Verificar se o CPF tem 11 dígitos
        if len(cpf) != 11:
            raise forms.ValidationError("CPF inválido")

        # Verificar se todos os dígitos do CPF são iguais (ex: 111.111.111-11)
        if len(set(cpf)) == 1:
            raise forms.ValidationError("CPF inválido")

        # Calcular o primeiro dígito verificador do CPF
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito1 = (soma * 10) % 11
        if digito1 == 10:
            digito1 = 0

        # Verificar se o primeiro dígito verificador está correto
        if digito1 != int(cpf[9]):
            raise forms.ValidationError("CPF inválido")

        # Calcular o segundo dígito verificador do CPF
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito2 = (soma * 10) % 11
        if digito2 == 10:
            digito2 = 0

        # Verificar se o segundo dígito verificador está correto
        if digito2 != int(cpf[10]):
            raise forms.ValidationError("CPF inválido")

        return cpf
