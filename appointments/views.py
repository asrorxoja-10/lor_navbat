import datetime
from datetime import datetime as dt, date, time, timedelta
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import TimeSlot, Appointment


def home_view(request):
    hozir = timezone.now()
    bugun = hozir.date()
    hozirgi_vaqt = hozir.time()

    if request.method == "POST":
        name = request.POST.get('patient_name')
        phone = request.POST.get('phone_number')
        complaint = request.POST.get('description', '')
        slot_id = request.POST.get('slot_id')

        if not name or not phone:
            messages.error(request, "Iltimos, barcha majburiy maydonlarni to'ldiring!")
            return redirect('home')

        if slot_id:
            slot = get_object_or_404(TimeSlot, id=slot_id)
        else:
            slot = TimeSlot.objects.filter(date__gte=bugun, is_booked=False).order_by('date', 'time').first()

        if not slot:
            messages.error(request, "Kechirasiz, hozircha qabul uchun bo'sh vaqtlar qolmagan!")
            return redirect('home')

        # ENG ASOSIY TEKSHIRUV: Agar vaqt band bo'lsa, qayta olishga yo'l qo'ymaydi
        if slot.is_booked:
            messages.error(request, "Afsuski, bu vaqt allaqachon boshqa fuqaro tomonidan band qilingan!")
            return redirect('home')

        # Navbatni yaratish
        Appointment.objects.create(
            slot=slot,
            patient_name=name,
            patient_phone=phone,
            complaint=complaint
        )

        # Vaqtni band holatga o'tkazish va saqlash
        slot.is_booked = True
        slot.save()

        soat_matni = slot.time.strftime('%H:%M')
        sana_matni = slot.date.strftime('%d-%m-%Y')

        messages.success(request, f"Muvaffaqiyatli! Siz {sana_matni} kuni soat {soat_matni} dagi qabulga muvaffaqiyatli navbat oldingiz.")
        return redirect('home')

    # FAQAT band qilinmagan (is_booked=False) va kelajakdagi vaqtlar ro'yxatini olish
    all_slots = TimeSlot.objects.filter(date__gte=bugun, is_booked=False).order_by('date', 'time')
    slots = [s for s in all_slots if not (s.date == bugun and s.time < hozirgi_vaqt)]

    return render(request, 'appointments/home.html', {'slots': slots})


def generate_new_slots_view(request):
    hozir = timezone.now()
    bugun = hozir.date()
    hozirgi_vaqt = hozir.time()

    TimeSlot.objects.filter(is_booked=False).delete()
    yangi_slotlar = []

    for i in range(30):
        qabul_kuni = bugun + timedelta(days=i)
        boshlanish = dt.combine(date.today(), time(9, 0))
        tugash = dt.combine(date.today(), time(21, 0))
        interval = timedelta(minutes=60)

        joriy = boshlanish
        while joriy <= tugash:
            slot_vaqti = joriy.time()

            if qabul_kuni == bugun and slot_vaqti < hozirgi_vaqt:
                joriy += interval
                continue

            if not TimeSlot.objects.filter(date=qabul_kuni, time=slot_vaqti).exists():
                yangi_slotlar.append(TimeSlot(date=qabul_kuni, time=slot_vaqti, is_booked=False))

            joriy += interval

    TimeSlot.objects.bulk_create(yangi_slotlar)
    messages.success(request, "Toshloq tuman hokimi qabuli uchun 30 kunlik yeni qabul soatlari muvaffaqiyatli yaratildi!")
    return redirect('home')


@login_required(login_url='/admin/login/')
def admin_dashboard_view(request):
    appointments = Appointment.objects.select_related('slot').all().order_by('slot__date', 'slot__time')
    return render(request, 'appointments/admin_dashboard.html', {'appointments': appointments})