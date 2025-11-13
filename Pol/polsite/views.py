from django.shortcuts import render
from .models import Partners, PartnerProducts, Products

def main_page_view(request):
    partners = Partners.objects.all()
    return render(request, 'mainpage.html', {'partners':partners})

def editadd_page_view(request):
    partners = Partners.objects.all()
    return render(request, 'editaddpage.html', {'partners':partners})

def history_page_view(request):
    partner_products = PartnerProducts.objects.select_related('partner','product').all()
    return render(request, 'history.html', {'partner_products':partner_products})