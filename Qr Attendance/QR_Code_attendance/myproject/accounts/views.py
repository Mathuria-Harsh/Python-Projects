from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import Employee
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def manage_employees(request):
    message = None

    if request.method == "POST":
        name = request.POST.get("username")
        employee_id = request.POST.get("employee_id")

        if Employee.objects.filter(employee_id=employee_id).exists():
            message = "Employee ID already exists"
        else:
            Employee.objects.create(
                name=name,
                employee_id=employee_id
            )
            return redirect('manage_employees')

    employees = Employee.objects.all()
    return render(request, "manage_employees.html", {
        "employees": employees,
        "message": message
    })


@staff_member_required(login_url='login')
def delete_employee(request, emp_id):
    emp = get_object_or_404(Employee, id=emp_id)
    emp.delete()
    return redirect('manage_employees')


def login_view(request):
    message = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('dashboard')

        else:
            message = "incorrect details, Please enter correct details"
    
    return render(request, "login.html", {"message":message})


def logout_view(request):
    logout(request)
    return redirect('login')