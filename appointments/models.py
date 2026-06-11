from django.db import models

class TimeSlot(models.Model):
    date = models.DateField(verbose_name="Qabul kuni")
    time = models.TimeField(verbose_name="Qabul vaqti")
    is_booked = models.BooleanField(default=False, verbose_name="Band qilinganmi")

    class Meta:
        verbose_name = "Qabul vaqti"
        verbose_name_plural = "Hokimiyat qabul vaqtlari"

    def __str__(self):
        return f"{self.date} | {self.time.strftime('%H:%M')}"


class Appointment(models.Model):
    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, verbose_name="Belgilangan vaqt sloti")
    # Bazadagi ma'lumotlar saqlanishi uchun o'zgaruvchi nomlari qoldi, lekin admin paneldagi nomlari tozalandi:
    patient_name = models.CharField(max_length=100, verbose_name="Fuqaro F.I.O")
    patient_phone = models.CharField(max_length=20, verbose_name="Fuqaro telefon raqami")
    complaint = models.TextField(blank=True, verbose_name="Murojaat/Muammo mazmuni")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yozilgan sana")

    class Meta:
        verbose_name = "Fuqaro arizasi"
        verbose_name_plural = "Kelib tushgan murojaatlar (Navbatlar)"

    def __str__(self):
        return f"{self.patient_name} - {self.slot.date}"