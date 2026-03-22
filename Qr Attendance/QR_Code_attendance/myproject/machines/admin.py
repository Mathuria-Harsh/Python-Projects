from django.contrib import admin
from .models import Machine
from django.utils.html import format_html

# Register your models here.

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('machine_name', 'machine_code', 'qr_preview')

    def qr_preview(self, obj):
        if obj.qr_image:
            return format_html(
                '<a href="{}" download><img src="{}" width="100" /></a>',
                obj.qr_image.url,
                obj.qr_image.url
            )
        return "No QR"

    qr_preview.short_description = "QR Code"