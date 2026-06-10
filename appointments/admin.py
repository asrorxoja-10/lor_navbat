from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import path
from .models import TimeSlot, Appointment

admin.site.site_header = "🏛️ Toshloq tuman hokimligi qabulxona tizimi"
admin.site.site_title = "Toshloq tuman hokimi qabuli"
admin.site.index_title = "Fuqarolar murojaatlari va qabul navbatlari"

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'is_booked')
    list_filter = ('date', 'is_booked')
    ordering = ('date', 'time')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'patient_phone', 'get_date', 'get_time')
    search_fields = ('patient_name', 'patient_phone')

    def get_date(self, obj): return obj.slot.date
    get_date.short_description = "Qabul kuni"

    def get_time(self, obj): return obj.slot.time
    get_time.short_description = "Qabul vaqti"