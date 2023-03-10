from ecommerce.inventory.models import Brand, Category


def categories(request):
    return {"categories": Category.objects.filter(parent=None)}


def scategories(request):
    return {"categories": Category.objects.filter(parent__isnull=False)}


def brands(request):
    return {"brands": Brand.objects.all}
