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
from django.contrib import messages
from .models import Employee, Payslip

# Create your views here.

# Employee Page
@login_required
def employee_list(request):
    if not request.user.is_staff:
        return redirect('payslips')

    employees = Employee.objects.all()
    return render(request, 'payroll_app/employees.html', {'employees': employees})

# Delete Employeee
@login_required
def delete_employee(request, pk):
    if not request.user.is_staff:
        return redirect('payslips')

    employee = get_object_or_404(Employee, pk=pk)
    employee.delete()
    return redirect('employee_list')

# Add Overtime
@login_required
def add_overtime(request, pk):
    if not request.user.is_staff:
        return redirect('payslips')

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
    if not request.user.is_staff:
        return redirect('payslips')

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
    if not request.user.is_staff:
        return redirect('payslips')

    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        name = request.POST.get('name', '')
        rate = request.POST.get('rate', '')
        allowance = request.POST.get('allowance', '') or 0
        overtime_pay = request.POST.get('overtime_pay', '') or 0

        if not all([name, rate]):
            return render(request, 'payroll_app/update_employee.html', {'employee': employee,'error': 'Please fill in required fields'})
        try:
            rate = float(rate)
            allowance = float(allowance)
            overtime_pay = float(overtime_pay)
        except ValueError:
            return render(request, 'payroll_app/update_employee.html', {'employee': employee,'error': 'Invalid input'})

        if allowance < 0 or overtime_pay < 0:
            return render(request, 'payroll_app/update_employee.html', {
                'employee': employee,
                'error': 'Allowance and overtime cannot be negative'
            })

        employee.rate = rate
        employee.allowance = allowance
        employee.overtime_pay = overtime_pay
        employee.name = name
        employee.save()

        return redirect('employee_list')

    return render(request, 'payroll_app/update_employee.html', {'employee': employee})

# Payslips Page
@login_required
def payslips_view(request):
    if request.user.is_staff:
        payslips = Payslip.objects.all()
        employees = Employee.objects.all()
    else:
        try:
            employee = Employee.objects.get(user=request.user)
            payslips = Payslip.objects.filter(id_number=employee)
            employees = Employee.objects.filter(user=request.user)
        except Employee.DoesNotExist:
            payslips = Payslip.objects.none()
            employees = Employee.objects.none()

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    if request.method == 'POST' and not request.user.is_staff:
        return redirect('payslips')
    
    if request.method == 'POST':
        payroll_for = request.POST.get('payroll_for')
        month = request.POST.get('month')
        year = request.POST.get('year')
        cycle = int(request.POST.get('cycle'))

        date_range = f"1-15" if cycle == 1 else f"16-{get_days_in_month(month)}"
        
        if payroll_for == 'all':
            target_employees = list(employees)
        else:
            target_employees = list(employees.filter(id_number=payroll_for))

        errors = []
        
        for emp in target_employees:
            already_exists = Payslip.objects.filter(id_number=emp, month=month, year=year, pay_cycle=cycle).exists()
            if already_exists:
                errors.append(f"Payslip already exists for {emp.name} ({emp.id_number}) — {month} {year} Cycle {cycle}")
                continue

            rate = emp.rate
            allowance = emp.allowance or 0
            overtime = emp.overtime_pay or 0
            half_rate = rate / 2

            if cycle == 1:
                pag_ibig = 100
                philhealth = 0
                sss = 0
                tax = (half_rate + allowance + overtime - pag_ibig) * 0.2
                total_pay = (half_rate + allowance + overtime - pag_ibig) - tax
            else:
                pag_ibig = 0
                philhealth = rate * 0.04
                sss = rate * 0.045
                tax = (half_rate + allowance + overtime - philhealth - sss) * 0.2
                total_pay = (half_rate + allowance + overtime - philhealth - sss) - tax

            Payslip.objects.create(
                id_number=emp,
                month=month,
                date_range=date_range,
                year=year,
                pay_cycle=cycle,
                rate=rate,
                earnings_allowance=allowance,
                deductions_tax=tax,
                deductions_health=philhealth,
                pag_ibig=pag_ibig,
                sss=sss,
                overtime=overtime,
                total_pay=total_pay
            )
            emp.resetOvertime()

        for err in errors:
            messages.error(request, err)

        return redirect('payslips')
    
    context = {
        'payslips': payslips,
        'employees': employees,
        'months': months,
    }
    return render(request, 'payroll_app/payslips.html', context)

def get_days_in_month(month_name):
    days = {
        'January': 31,
        'February': 28,
        'March': 31,
        'April': 30,
        'May': 31,
        'June': 30,
        'July': 31,
        'August': 31,
        'September': 30,
        'October': 31,
        'November': 30,
        'December': 31
    }
    return days.get(month_name, 30)

# View Payslip
@login_required
def view_payslip(request, pk):
    payslip = get_object_or_404(Payslip, pk=pk)
    
    if not request.user.is_staff:
        try:
            employee = Employee.objects.get(user=request.user)
            if payslip.id_number != employee:
                return redirect('payslips')
        except Employee.DoesNotExist:
            return redirect('payslips')
        
    return render(request, 'payroll_app/view_payslip.html', {'payslip': payslip})

