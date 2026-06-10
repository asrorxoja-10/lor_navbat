from django.urls import path
from .views import home_view, generate_new_slots_view
from . import views
urlpatterns = [
    path('', home_view, name='home'),

    # Yangi 30 daqiqalik qabul vaqtlarini generatsiya qiluvchi maxsus manzil
    path('generate-slots-secret/', generate_new_slots_view, name='generate_slots'),
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
]