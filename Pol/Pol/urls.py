from django.urls import path
from polsite import views

urlpatterns = [
    path('', views.main_page_view, name='main_page'),
    path('editadd/', views.editadd_page_view, name='editadd_page'),  # Добавление (без ID)
    path('editadd/<int:partner_id>/', views.editadd_page_view, name='edit_partner'),  # Редактирование (с ID)
    path('history/', views.history_page_view, name='history_page'),
]