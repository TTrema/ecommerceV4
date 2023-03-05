from ecommerce.inventory.models import Category, Brand

def categories(request):
    return {"categories": Category.objects.filter(parent=None)}

def scategories(request):
    return {"categories": Category.objects.filter(parent__isnull=False)}

def brands(request):
    return {"brands": Brand.objects.all}