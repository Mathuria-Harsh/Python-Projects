from django.db import models
from accounts.models import Employee
from machines.models import Machine

# Create your models here.

class MachineCheck(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.machine}"
    