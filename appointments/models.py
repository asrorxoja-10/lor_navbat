from django.db import models

class TimeSlot(models.Model):
    """Shifokorning qabul vaqtlari (masalan: 09:00, 09:30)"""
    date = models.DateField(verbose_name="Sana")
    time = models.TimeField(verbose_name="Soat")
    is_booked = models.BooleanField(default=False, verbose_name="Band qilingan")

    class Meta:
        verbose_name = "Vaqt katakchasi"
        verbose_name_plural = "Vaqt katakchalari"
        ordering = ['date', 'time']

    def __str__(self):
        status = "Band" if self.is_booked else "Bo'sh"
        return f"{self.date} | {self.time.strftime('%H:%M')} ({status})"


class Appointment(models.Model):
    """Bemor olgan navbatlar"""
    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, verbose_name="Tanlangan vaqt")
    patient_name = models.CharField(max_length=100, verbose_name="Bemor ismi")
    patient_phone = models.CharField(max_length=20, verbose_name="Telefon raqami")
    complaint = models.TextField(verbose_name="Shikoyati", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Navbat"
        verbose_name_plural = "Navbatlar"

    def __str__(self):
        return f"{self.patient_name} - {self.slot.date} {self.slot.time.strftime('%H:%M')}"
