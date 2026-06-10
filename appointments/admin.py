from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import path
from django import forms
from django.utils.html import format_html
import datetime
from .models import TimeSlot

# --- ADMIN PANEL INTERFEYSINI BRENDLASH ---
admin.site.site_header = "🏛️ Toshloq tuman hokimligi qabulxona tizimi"
admin.site.site_title = "Toshloq tuman hokimi qabuli"
admin.site.index_title = "Fuqarolar murojaatlari va qabul navbatlari"

# Vaqt generator formasi (09:00 dan 21:00 gacha, har 1 soatda)
class SlotGeneratorForm(forms.Form):
    date = forms.DateField(
        label="Qabul sanasi",
        widget=forms.SelectDateWidget(),
        initial=datetime.date.today
    )
    start_time = forms.TimeField(
        label="Qabul boshlanish vaqti",
        initial=datetime.time(9, 0)  # Soat 09:00 da boshlanadi
    )
    end_time = forms.TimeField(
        label="Qabul tugash vaqti",
        initial=datetime.time(21, 0)  # Kechki 21:00 gacha uzaytirildi
    )
    duration_minutes = forms.IntegerField(
        label="Har bir fuqaroga ajratiladigan vaqt (daqiqa hisobida)",
        initial=60,  # Standart 1 soat (60 daqiqa) qilib belgilandi
        min_value=5
    )


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'is_booked', 'go_to_dashboard')
    list_filter = ('date', 'is_booked')
    ordering = ('date', 'time')

    change_list_template = "admin/appointments_change_list.html"

    def go_to_dashboard(self, obj):
        return format_html(
            '<a class="button" style="background-color: #1e3a8a; color: white; padding: 4px 10px; border-radius: 6px; font-weight: 600; text-decoration: none;" href="/dashboard/">Jadvalni ko\'rish 📊</a>'
        )
    go_to_dashboard.short_description = "Onlayn Navbatlar"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate-slots/', self.admin_site.admin_view(self.generate_slots_view), name='generate-slots'),
        ]
        return custom_urls + urls

    def generate_slots_view(self, request):
        if request.method == 'POST':
            form = SlotGeneratorForm(request.POST)
            if form.is_valid():
                date = form.cleaned_data['date']
                start_time = form.cleaned_data['start_time']
                end_time = form.cleaned_data['end_time']
                duration = form.cleaned_data['duration_minutes']

                current_datetime = datetime.datetime.combine(date, start_time)
                end_datetime = datetime.datetime.combine(date, end_time)

                slots_created = 0
                while current_datetime < end_datetime:
                    slot_time = current_datetime.time()

                    if not TimeSlot.objects.filter(date=date, time=slot_time).exists():
                        TimeSlot.objects.create(date=date, time=slot_time, is_booked=False)
                        slots_created += 1

                    current_datetime += datetime.timedelta(minutes=duration)

                self.message_user(request, f"Muvaffaqiyatli: {date} sana uchun {slots_created} ta qabul soatlari yaratildi!")
                return HttpResponseRedirect("../")
        else:
            form = SlotGeneratorForm()

        context = self.admin_site.each_context(request)
        context['form'] = form
        context['title'] = "Toshloq tuman hokimi qabuli - Vaqt Generator tizimi"
        return render(request, "admin/generate_slots.html", context)