import datetime
from datetime import datetime as dt, date, time, timedelta
import requests
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required  # Admin panelni himoya qilish uchun
from .models import TimeSlot, Appointment

# --- TELEGRAM BOT SOZLAMALARI ---
TELEGRAM_BOT_TOKEN = '7355604128:AAFn_Y_Xm_U1...'
TELEGRAM_CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID'

# --- ESKIZ.UZ SMS SOZLAMALARI ---
ESKIZ_EMAIL = "Sizning_Eskiz_Emailingiz@gmail.com"
ESKIZ_PASSWORD = "Sizning_Eskiz_Parolingiz"


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram error: {e}")


def get_eskiz_token():
    url = "https://notify.eskiz.uz/api/auth/login"
    payload = {'email': ESKIZ_EMAIL, 'password': ESKIZ_PASSWORD}
    try:
        response = requests.post(url, data=payload, timeout=5)
        if response.status_code == 200: return response.json().get('data', {}).get('token')
    except Exception as e:
        print(f"Eskiz token error: {e}")
    return None


def send_sms_notification(phone_number, message_text):
    token = get_eskiz_token()
    if not token: return False
    url = "https://notify.eskiz.uz/api/message/sms/send"
    headers = {'Authorization': f'Bearer {token}'}
    clean_phone = "".join(filter(str.isdigit, phone_number))
    payload = {
        'mobile_phone': clean_phone,
        'message': message_text,
        'from': '4545',
        'callback_url': 'http://0000.uz/test.php'
    }
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"SMS error: {e}"); return False


def home_view(request):
    hozir = timezone.now()
    bugun = hozir.date()
    hozirgi_vaqt = hozir.time()

    if request.method == "POST":
        slot_id = request.POST.get('slot_id')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        complaint = request.POST.get('complaint', '')

        if not slot_id or not name or not phone:
            messages.error(request, "Iltimos, barcha majburiy maydonlarni to'ldiring!")
            return redirect('home')

        slot = get_object_or_404(TimeSlot, id=slot_id)

        if slot.is_booked:
            messages.error(request, "Afsuski, bu vaqt allaqachon band qilingan.")
            return redirect('home')

        if slot.date == bugun and slot.time < hozirgi_vaqt:
            messages.error(request, "Kechirasiz, bu vaqt qabul oynasi o'tib ketgan.")
            return redirect('home')

        Appointment.objects.create(slot=slot, patient_name=name, patient_phone=phone, complaint=complaint)
        slot.is_booked = True
        slot.save()

        soat_matni = slot.time.strftime('%H:%M')
        send_telegram_message(
            f"🔔 *YANGI NAVBAT!*\n\n👤 *Bemor:* {name}\n📅 *Sana:* {slot.date.strftime('%d-%m-%Y')}\n⏰ *Soat:* {soat_matni}")
        send_sms_notification(phone,
                              f"Dr. Akmalov LOR. {name}, tasdiqlandi: {slot.date.strftime('%d-%m')} soat {soat_matni}. Salomat bo'ling!")

        messages.success(request, f"Tabriklaymiz! Siz soat {soat_matni} ga muvaffaqiyatli navbat oldingiz.")
        return redirect('home')

    all_slots = TimeSlot.objects.filter(date__gte=bugun).order_by('date', 'time')

    slots = []
    for s in all_slots:
        if s.date == bugun:
            if s.time >= hozirgi_vaqt:
                slots.append(s)
        else:
            slots.append(s)

    dates = TimeSlot.objects.filter(date__gte=bugun).values_list('date', flat=True).distinct().order_by('date')

    context = {
        'slots': slots,
        'dates': dates,
    }
    return render(request, 'appointments/home.html', context)


def generate_new_slots_view(request):
    hozir = timezone.now()
    bugun = hozir.date()
    hozirgi_vaqt = hozir.time()

    TimeSlot.objects.filter(is_booked=False).delete()

    yangi_slotlar_ruyxati = []

    for i in range(30):
        qabul_kuni = bugun + timedelta(days=i)

        boshlanish_vaqti = dt.combine(date.today(), time(9, 0))  # 09:00
        tugash_vaqti = dt.combine(date.today(), time(22, 0))  # 22:00
        interval = timedelta(minutes=30)

        joriy_vaqt = boshlanish_vaqti
        while joriy_vaqt <= tugash_vaqti:
            slot_vaqti = joriy_vaqt.time()

            if qabul_kuni == bugun and slot_vaqti < hozirgi_vaqt:
                joriy_vaqt += interval
                continue

            if TimeSlot.objects.filter(date=qabul_kuni, time=slot_vaqti).exists():
                joriy_vaqt += interval
                continue

            yangi_slotlar_ruyxati.append(
                TimeSlot(date=qabul_kuni, time=slot_vaqti, is_booked=False)
            )
            joriy_vaqt += interval

    TimeSlot.objects.bulk_create(yangi_slotlar_ruyxati)

    messages.success(request, "30 kunlik yangi ish jadvali muvaffaqiyatli yangilandi!")
    return redirect('home')


# --- YANGI QO'SHILGAN ADMIN PANEL (DASHBOARD) FUNKSIYASI ---
@login_required(login_url='/admin/login/')  # Shifokor tizimga kirmagan bo'lsa, login sahifasiga otadi
def admin_dashboard_view(request):
    hozir = timezone.now()
    bugun = hozir.date()

    # Barcha onlayn yozilgan bemorlarni eng yaqin kun va soat bo'yicha saralab olamiz
    # select_related orqali bog'langan slot ma'lumotlarini bazadan birdiga tortamiz (tez ishlashi uchun)
    appointments = Appointment.objects.select_related('slot').all().order_by('slot__date', 'slot__time')

    # Dashboard yuqorisidagi widgetlar uchun statistika ma'lumotlari
    total_booked = appointments.count()
    today_booked = Appointment.objects.filter(slot__date=bugun).count()
    total_free = TimeSlot.objects.filter(date__gte=bugun, is_booked=False).count()

    context = {
        'appointments': appointments,
        'total_booked': total_booked,
        'today_booked': today_booked,
        'total_free': total_free,
    }
    return render(request, 'appointments/admin_dashboard.html', context)