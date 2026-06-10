from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('generate-slots/', views.generate_new_slots_view, name='generate_slots'),
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
]