from django.contrib import admin
from .models import TimeSlot, Appointment

# Admin panel sarlavhalaridan "Lor" so'zini butunlay yo'qotish:
admin.site.site_header = "Toshloq tuman hokimligi qabulxona tizimi"
admin.site.site_title = "Hokimiyat Admin"
admin.site.index_title = "Fuqarolar murojaatlari va qabul navbatlari"

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'is_booked')
    list_filter = ('date', 'is_booked')
    ordering = ('date', 'time')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'patient_phone', 'get_date', 'get_time', 'created_at')
    search_fields = ('patient_name', 'patient_phone', 'complaint')
    list_filter = ('slot__date',)

    # Jadvalda vaqt va sanani alohida ustun qilib ko'rsatish
    def get_date(self, obj):
        return obj.slot.date
    get_date.short_description = 'Qabul kuni'

    def get_time(self, obj):
        return obj.slot.time.strftime('%H:%M')
    get_time.short_description = 'Qabul vaqti'