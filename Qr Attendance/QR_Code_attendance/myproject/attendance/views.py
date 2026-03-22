from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from machines.models import Machine
from accounts.models import Employee
from .models import MachineCheck
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from collections import defaultdict, OrderedDict

# Create your views here.

def check_machine(request, machine_code):
    machine = get_object_or_404(Machine, machine_code=machine_code)

    if request.method == "POST":
        employee_id = request.POST.get("employee_id")

        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return render(request, "enter_employee_id.html", {
                "machine": machine,
                "error": "Invalid Employee ID"
            })

        now = timezone.now()
        today = now.date()

        # Get today's checks
        today_checks = MachineCheck.objects.filter(
            employee=employee,
            machine=machine,
            date=today
        ).order_by('time')

        # Max 4 checks rule
        if today_checks.count() >= 4:
            return render(request, "scan_result.html", {
                "machine": machine,
                "status": "Shift Completed (4/4 checks done)",
                "current_time": now
            })

        # 2 hour gap rule
        if today_checks.exists():
            last_check = today_checks.last()

            last_time = timezone.make_aware(
                timezone.datetime.combine(last_check.date, last_check.time)
            )

            if now - last_time < timedelta(hours=2):
                return render(request, "scan_result.html", {
                    "machine": machine,
                    "status": "Wait for 2 hours before next check",
                    "current_time": now
                })

        # Allow scan
        record = MachineCheck.objects.create(
            employee=employee,
            machine=machine
        )

        count = today_checks.count() + 1

        return render(request, "scan_result.html", {
            "machine": machine,
            "employee": employee,
            "record": record,
            "status": f"Check Recorded ({count}/4)",
            "current_time": now
        })

    return render(request, "enter_employee_id.html", {"machine": machine})


def home(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard')
    return redirect('login')


@staff_member_required(login_url='login')
def dashboard(request):

    now = timezone.now()
    today = now.date()

    # All records (latest first)
    all_records = MachineCheck.objects.select_related(
        'employee', 'machine'
    ).order_by('-date', '-time')

    # Only latest record per machine
    latest_records = OrderedDict()

    for record in all_records:
        if record.machine.id not in latest_records:
            latest_records[record.machine.id] = record

    records = list(latest_records.values())

    # Timer + Count logic (It will run first)
    for record in records:

        last_time = timezone.make_aware(
            timezone.datetime.combine(record.date, record.time)
        )

        next_check_time = last_time + timedelta(hours=2)
        remaining_time = next_check_time - now

        # Timer status
        if remaining_time.total_seconds() > 0:
            record.remaining_seconds = int(remaining_time.total_seconds())
            record.timer_done = False
        else:
            record.remaining_seconds = 0
            record.timer_done = True

        # Count logic
        record.check_count = MachineCheck.objects.filter(
            employee=record.employee,
            machine=record.machine,
            date=today
        ).count()

    
    recheck_records = [record for record in records if record.timer_done]

    return render(request, 'dashboard.html', {
        'records': records,
        'recheck_records': recheck_records
    })
            

# to get latest record of an employee
# @staff_member_required(login_url='login')
# def dashboard(request):
#     records = MachineCheck.objects.select_related('employee', 'machine').order_by('-date', '-time')   # latest first (recommended)

#     return render(request, 'dashboard.html', {
#         'records': records
#     })
