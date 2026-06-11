import datetime
from datetime import datetime as dt, date, time, timedelta
import urllib.parse
import urllib.request
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
        # HTML formadan kelayotgan qiymatlarni olish
        name = request.POST.get('patient_name')
        phone = request.POST.get('phone_number')
        complaint = request.POST.get('description', '')
        slot_id = request.POST.get('slot_id')

        # Maydonlar bo'shligini tekshirish
        if not name or not phone or not slot_id:
            messages.error(request, "Iltimos, ism, telefon va vaqtni to'liq kiriting!")
            return redirect('home')

        try:
            # Vaqt slotini olish
            slot = TimeSlot.objects.get(id=slot_id)

            # Agar vaqt allaqachon band bo'lsa
            if slot.is_booked or hasattr(slot, 'appointment'):
                messages.error(request, "Afsuski, bu vaqt band qilingan! Boshqa vaqt tanlang.")
                return redirect('home')

            # BAZAGA MUVAFFAQIYATLI YOZISH
            new_appointment = Appointment()
            new_appointment.slot = slot
            new_appointment.patient_name = name
            new_appointment.patient_phone = phone
            new_appointment.complaint = complaint
            new_appointment.save()

            # 🚀 TELEGRAM BOT ORQALI XABARNOMA YUBORISH (SIZNING BOTINGIZ SOZLANDI)
            try:
                BOT_TOKEN = "8909170695:AAGHLEDm6j3k0cPA6Jj_8KdgjQ3rwFvSIik"
                CHAT_ID = "6087478497"

                sana_matni = slot.date.strftime('%d-%m-%Y')
                soat_matni = slot.time.strftime('%H:%M')

                # Telegramga boradigan rasmiy xabar matni
                text = (
                    f"🏛️ *YANGI MUROJAAT KELIB TUSHDI!*\n\n"
                    f"👤 *Fuqaro F.I.O:* {name}\n"
                    f"📞 *Telefon raqami:* {phone}\n"
                    f"🗓️ *Belgilangan vaqt:* {sana_matni} | Soat: {soat_matni}\n"
                    f"📝 *Murojaat mazmuni:* {complaint if complaint else 'Kiritilmagan'}"
                )

                # Telegram API orqali so'rov yuborish
                encoded_text = urllib.parse.quote(text)
                telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={encoded_text}&parse_mode=Markdown"

                req = urllib.request.Request(telegram_url, headers={'User-Agent': 'Mozilla/5.0'})
                urllib.request.urlopen(req)
            except Exception as telegram_error:
                # Agar telegramda uzilish bo'lsa sayt qotib qolmasligi uchun xatoni o'tkazib yuboramiz
                pass
            # 🚀 TELEGRAM LOGIKASI TUGADI

            # Vaqtni band deb belgilash
            slot.is_booked = True
            slot.save()

            sana_matni = slot.date.strftime('%d-%m-%Y')
            soat_matni = slot.time.strftime('%H:%M')

            messages.success(request,
                             f"Muvaffaqiyatli! Siz {sana_matni} kuni soat {soat_matni} dagi qabulga navbat oldingiz.")
            return redirect('home')

        except TimeSlot.DoesNotExist:
            messages.error(request, "Xatolik: Bunday qabul vaqti topilmadi!")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {e}")
            return redirect('home')

    # Faqat bugungi va kelajakdagi band bo'lmagan vaqtlar
    all_slots = TimeSlot.objects.filter(date__gte=bugun, is_booked=False).order_by('date', 'time')
    slots = [s for s in all_slots if not (s.date == bugun and s.time < hozirgi_vaqt)]

    return render(request, 'appointments/home.html', {'slots': slots})


@login_required(login_url='/admin/login/')
def admin_dashboard_view(request):
    if request.method == "POST" and "delete_id" in request.POST:
        appointment_id = request.POST.get("delete_id")
        app = get_object_or_404(Appointment, id=appointment_id)
        if app.slot:
            app.slot.is_booked = False  # Vaqtni qayta ochish
            app.slot.save()
        app.delete()
        messages.success(request, "Murojaat muvaffaqiyatli o'chirildi!")
        return redirect('admin_dashboard')

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
    messages.success(request, "30 kunlik yangi qabul soatlari yaratildi!")
    return redirect('home')