# Site de ecommerce feito em Django

O front foi feito usando o template MDB5, disponível em https://mdbootstrap.com/freebies/e-commerce/.


## Demonstração:

Uma demonstração do site está disponivel em:

https://jwill.pythonanywhere.com/


## Características:

   <ul>
  <li>Carrinho de compras</li>
  <li>Vários endereços</li>
  <li>Sistema de cupom</li> 
  <li>Cálculo de frete usando a API dos Correios</li>
  <li>Busca de produtos com completamento automático</li>
  <li>Pagamento com Stripe e Paypal</li>
  <li>Sistema para pedido de reembolso</li>
  <li>Lista de desejos</li>
  </ul>
  
## Pré-requisitos:
   <ul>
   <li>Docker</li> 
   <li>Python</li>
   </ul>

Em caso de erro "connection to server at "127.0.0.1", port 5432 failed: FATAL: password authentication failed for user "postgres", será preciso primeiro desativar o serviço local do postgres.

## Instruções de uso:

## Crie e ative um virtual environment:

    Windows:
        Crie a venv usando o comando python -m venv nome_da_venv (exemplo: python -m venv venv).
        Ative a venv usando o comando .\nome_da_venv\Scripts\activate (exemplo: .\venv\Scripts\activate).

    Linux e macOS:
        Crie a venv usando o comando python3 -m venv nome_da_venv (exemplo: python3 -m venv venv).
        Ative a venv usando o comando source nome_da_venv/bin/activate (exemplo: source venv/bin/activate).

### Use o comando:

    pip install -r requirements.txt

### Use o comando para iniciar o banco de dados em Postgres (precisa estar com o Docker ativo e funcionando):

    docker-compose up

### Coloque suas credenciais

    Preencha as KEYS do Django, Paypal e Stripe com suas credenciais no arquivo keys.py.

### Use os comandos:

    python manage.py makemigrations
    python manage.py migrate

### Ou use apenas o comando que faz as migrações e preenche o banco de dados com categorias e produtos:

    python manage.py load-mixtures

### Use o comando:

    python manage.py runserver


