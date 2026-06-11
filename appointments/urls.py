from django.urls import path
from appointments.views import home_view, admin_dashboard_view, generate_new_slots_view

urlpatterns = [
    path('', home_view, name='home'),
    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('generate-slots/', generate_new_slots_view, name='generate_slots'),
]