from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
# Django login system free, employee can be easily identify

class Employee(models.Model):
    name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"


@receiver(post_save, sender=User)
def create_employee(sender, instance, created, **kwargs):
    if created:
        Employee.objects.create(
            user=instance,
            employee_id=f"EMP{instance.id:03}"
        )
        