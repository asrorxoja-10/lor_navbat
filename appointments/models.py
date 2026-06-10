from django.db import models

class TimeSlot(models.Model):
    date = models.DateField(verbose_name="Qabul kuni")
    time = models.TimeField(verbose_name="Qabul vaqti")
    is_booked = models.BooleanField(default=False, verbose_name="Band qilinganmi")

    class Meta:
        verbose_name = "Vaqt Sloti"
        verbose_name_plural = "Qabul Vaqt Slotlari"

    def __str__(self):
        return f"{self.date} | {self.time.strftime('%H:%M')}"


class Appointment(models.Model):
    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, verbose_name="Vaqt sloti")
    patient_name = models.CharField(max_length=100, verbose_name="Fuqaro F.I.O")
    patient_phone = models.CharField(max_length=20, verbose_name="Telefon raqami")
    complaint = models.TextField(blank=True, verbose_name="Murojaat mazmuni")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Qabul navbati"
        verbose_name_plural = "Fuqarolar qabuli (Navbatlar)"

    def __str__(self):
        return f"{self.patient_name} - {self.slot.date}"