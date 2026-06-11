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

        # Maydonlarni tekshirish
        if not name or not phone or not slot_id:
            messages.error(request, "Iltimos, barcha maydonlarni to'ldiring va vaqtni tanlang!")
            return redirect('home')

        # Tanlangan vaqtni olish
        slot = get_object_or_404(TimeSlot, id=slot_id)

        # Vaqt bandligini tekshirish
        if slot.is_booked:
            messages.error(request, "Afsuski, bu vaqt allaqachon band qilingan! Boshqa vaqtni tanlang.")
            return redirect('home')

        # BAZAGA SAQLASH (ENG ASOSIY QISM)
        Appointment.objects.create(
            slot=slot,
            patient_name=name,
            patient_phone=phone,
            complaint=complaint
        )

        # Vaqtni band deb belgilash va saqlash
        slot.is_booked = True
        slot.save()

        soat_matni = slot.time.strftime('%H:%M')
        sana_matni = slot.date.strftime('%d-%m-%Y')

        messages.success(request, f"Muvaffaqiyatli! Siz {sana_matni} kuni soat {soat_matni} dagi qabulga navbat oldingiz.")
        return redirect('home')

    # Faqat band bo'lmagan slotlarni shablonga chiqarish
    all_slots = TimeSlot.objects.filter(date__gte=bugun, is_booked=False).order_by('date', 'time')
    slots = [s for s in all_slots if not (s.date == bugun and s.time < hozirgi_vaqt)]

    return render(request, 'appointments/home.html', {'slots': slots})


@login_required(login_url='/admin/login/')
def admin_dashboard_view(request):
    # Arizani o'chirish
    if request.method == "POST" and "delete_id" in request.POST:
        appointment_id = request.POST.get("delete_id")
        app = get_object_or_404(Appointment, id=appointment_id)
        if app.slot:
            app.slot.is_booked = False  # Vaqtni qayta bo'shatish
            app.slot.save()
        app.delete()
        messages.success(request, "Murojaat muvaffaqiyatli o'chirildi va vaqt qayta ochildi!")
        return redirect('admin_dashboard')

    # Barcha arizalarni olish
    appointments = Appointment.objects.select_related('slot').all().order_by('slot__date', 'slot__time')
    return render(request, 'appointments/admin_dashboard.html', {'appointments': appointments})


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
    messages.success(request, "30 kunlik yangi bo'sh qabul soatlari muvaffaqiyatli yaratildi!")
    return redirect('home')