# Tashannah Doller, 245541 ; Gide Ng, ; Nathan Riley Sy, 244311
# April , 2026

'''
I hereby attest to the truth of the following facts:

I have not discussed the Python language code in my program with anyone
other than my instructor or the teaching assistants assigned to this course.

I have not used Python language code obtained from another student, or
any other unauthorized source, either modified or unmodified.

If any Python language code or documentation used in my program was
obtained from another source, such as a textbook or course notes, that has been clearly noted with proper citation in the
comments of my program.
'''

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Employee
from .forms import EmployeeForm

# Create your views here.

def test_page(request): # this is only to test the base. remove once completed
    return render(request, 'payroll_app/base.html')

# Employee Page
@login_required(login_url='login')
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'payroll_app/employees.html', {'employees': employees})

# Delete Employeee
@login_required(login_url='login')
def delete_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.delete()
    return redirect('employee_list')

# Add Overtime
@login_required(login_url='login')
def add_overtime(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == "POST":
        hours = request.POST.get('hours')

        try:
            hours = float(hours)
        except (TypeError, ValueError):
            hours = 0

        overtime_amount = (employee.rate / 160) * 1.5 * hours
        employee.overtime_pay = (employee.overtime_pay or 0) + overtime_amount
        employee.save()

    return redirect('employee_list')

# Create Employee
@login_required
def create_employee(request):
    if request.method == "POST":
        name = request.POST.get('name', '')
        id_number = request.POST.get('id_number', '')
        rate = request.POST.get('rate', '')
        allowance = request.POST.get('allowance', '') or 0

        if not all([name, id_number, rate]):
            return render(request, 'payroll_app/create_employee.html', {'error': 'Please fill in all required fields'})

        try:
            rate = float(rate)
            allowance = float(allowance)
        except ValueError:
            return render(request, 'payroll_app/create_employee.html', {'error': 'Rate and allowance must be valid numbers'})

        if Employee.objects.filter(id_number=id_number).exists():
            return render(request, 'payroll_app/create_employee.html', {'error': 'Employee ID already exists'})

        Employee.objects.create(name=name, id_number=id_number, rate=rate,allowance=allowance)

        return redirect('employee_list')

    return render(request, 'payroll_app/create_employee.html')

# Update Employee
@login_required
def update_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        name = request.POST.get('name', '')
        rate = request.POST.get('rate', '')
        allowance = request.POST.get('allowance', '') or 0
        overtime_pay = request.POST.get('overtime_pay', '') or 0

        if not all([name, rate]):
            return render(request, 'payroll_app/update_employee.html', {'employee': employee,'error': 'Please fill in required fields'})

        try:
            employee.rate = float(rate)
            employee.allowance = float(allowance)
            employee.overtime_pay = float(overtime_pay)
        except ValueError:
            return render(request, 'payroll_app/update_employee.html', {'employee': employee,'error': 'Invalid input'})

        employee.name = name
        employee.save()

        return redirect('employee_list')
    return render(request, 'payroll_app/update_employee.html', {'employee': employee})
