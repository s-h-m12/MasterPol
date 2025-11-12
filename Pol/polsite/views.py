from django.shortcuts import render
from .models import Partners

def main_page_view(request):
    partners = Partners.objects.all()
    return render(request, 'mainpage.html', {'partners':partners})
