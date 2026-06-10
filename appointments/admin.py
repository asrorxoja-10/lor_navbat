from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import path
from django import forms
from django.utils.html import format_html  # Tugmalarni xavfsiz render qilish uchun
import datetime
from .models import TimeSlot

# --- ADMIN PANEL INTERFEYSINI BRENDLASH ---
admin.site.site_header = "Dr. Akmalov LOR | Admin Boshqaruv"
admin.site.site_title = "Shifokor Paneli"
admin.site.index_title = "Tizim ma'lumotlari boshqaruvi"


# Avtomatik vaqt yaratish uchun maxsus forma
class SlotGeneratorForm(forms.Form):
    date = forms.DateField(
        label="Qabul sanasi",
        widget=forms.SelectDateWidget(),
        initial=datetime.date.today
    )
    start_time = forms.TimeField(
        label="Ish boshlanish vaqti",
        initial=datetime.time(9, 0)  # standart 09:00
    )
    end_time = forms.TimeField(
        label="Ish tugash vaqti",
        initial=datetime.time(17, 0)  # standart 17:00
    )
    duration_minutes = forms.IntegerField(
        label="Har bir bemorga ajratiladigan vaqt (minutda)",
        initial=30,
        min_value=5
    )


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    # Jadvalda chiroyli ko'rinishi uchun go_to_dashboard ham qo'shildi
    list_display = ('date', 'time', 'is_booked', 'go_to_dashboard')
    list_filter = ('date', 'is_booked')
    ordering = ('date', 'time')

    # Admin panelga yangi tugma va sahifa havolasini qo'shamiz
    change_list_template = "admin/appointments_change_list.html"

    # Har bir qator yonida maxsus dizayndagi "Dashboard"ga o'tish tugmasi
    def go_to_dashboard(self, obj):
        return format_html(
            '<a class="button" style="background-color: #4f46e5; color: white; padding: 4px 10px; border-radius: 6px; font-weight: 600; text-decoration: none;" href="/dashboard/">Jadvalni ko\'rish 📊</a>'
        )
    go_to_dashboard.short_description = "Onlayn Navbatlar"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate-slots/', self.admin_site.admin_view(self.generate_slots_view), name='generate-slots'),
        ]
        return custom_urls + urls

    # Vaqtni yaratish logikasi (Backend)
    def generate_slots_view(self, request):
        if request.method == 'POST':
            form = SlotGeneratorForm(request.POST)
            if form.is_valid():
                date = form.cleaned_data['date']
                start_time = form.cleaned_data['start_time']
                end_time = form.cleaned_data['end_time']
                duration = form.cleaned_data['duration_minutes']

                # Vaqtlarni hisoblash boshlanadi
                current_datetime = datetime.datetime.combine(date, start_time)
                end_datetime = datetime.datetime.combine(date, end_time)

                slots_created = 0
                while current_datetime < end_datetime:
                    slot_time = current_datetime.time()

                    # Agar bu vaqt oldindan bazada bo'lmasa, yangi ochamiz
                    if not TimeSlot.objects.filter(date=date, time=slot_time).exists():
                        TimeSlot.objects.create(date=date, time=slot_time, is_booked=False)
                        slots_created += 1

                    # Keyingi slot vaqtiga o'tish (+30 minut yoki berilgan muddat)
                    current_datetime += datetime.timedelta(minutes=duration)

                self.message_user(request,
                                  f"Muvaffaqiyatli: {date} sana uchun {slots_created} ta qabul vaqti yaratildi!")
                return HttpResponseRedirect("../")
        else:
            form = SlotGeneratorForm()

        context = self.admin_site.each_context(request)
        context['form'] = form
        context['title'] = "Avtomatik Vaqt Generator boti"
        return render(request, "admin/generate_slots.html", context)