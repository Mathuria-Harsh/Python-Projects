import qrcode
from io import BytesIO
from django.core.files import File
from django.db import models

class Machine(models.Model):
    machine_name = models.CharField(max_length=100)
    machine_code = models.CharField(max_length=50, unique=True)
    qr_image = models.ImageField(upload_to='machine_qr/', blank=True)

    def save(self, *args, **kwargs):
        qr_data = f"http://192.168.0.107:8000/check/{self.machine_code}/"
                           
        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')

        file_name = f"{self.machine_code}.png"
        self.qr_image.save(file_name, File(buffer), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.machine_name