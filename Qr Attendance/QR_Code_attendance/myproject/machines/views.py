from django.shortcuts import render, redirect, get_object_or_404
from .models import Machine
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.

@staff_member_required
def machine_create(request):
    if request.method == "POST":
        machine_name = request.POST.get("machine_name")
        machine_code = request.POST.get("machine_code")

        Machine.objects.create(
            machine_name = machine_name,
            machine_code = machine_code
        )

        return redirect('machine_create')
    
    machines = Machine.objects.all()

    return render(request, "machine_create.html", {"machines":machines})


@staff_member_required
def delete_machine(request, machine_id):
    machine = get_object_or_404(Machine, id = machine_id)
    machine.delete()
    return redirect('machine_create')
