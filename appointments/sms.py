import requests

ESKIZ_EMAIL = "Sizning_Eskiz_Emailingiz@gmail.com"  # Eskiz.uz dagi profilingiz emaili
ESKIZ_PASSWORD = "Sizning_Eskiz_Parolingiz"  # Eskiz.uz dagi parolingiz


def get_eskiz_token():
    """Eskiz API'dan vaqtinchalik JWT token olish"""
    url = "https://notify.eskiz.uz/api/auth/login"
    payload = {
        'email': ESKIZ_EMAIL,
        'password': ESKIZ_PASSWORD
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            return response.json().get('data', {}).get('token')
    except Exception as e:
        print(f"Token olishda xatolik: {e}")
    return None


def send_sms_notification(phone_number, message_text):
    """Bemorga SMS xabar yuborish"""
    token = get_eskiz_token()
    if not token:
        print("Xatolik: Eskiz tokenini olib bo'lmadi!")
        return False

    url = "https://notify.eskiz.uz/api/message/sms/send"
    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Telefon raqamni tozalash (faqat raqamlar qolishi kerak, masalan: 998901234567)
    clean_phone = "".join(filter(str.isdigit, phone_number))

    payload = {
        'mobile_phone': clean_phone,
        'message': message_text,
        'from': '4545',  # Eskiz taqdim etgan standart tekin login (yoki sizning maxsus nomingiz)
        'callback_url': 'http://0000.uz/test.php'
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"SMS yuborishda xatolik: {e}")
        return False