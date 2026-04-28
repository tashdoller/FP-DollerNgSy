# Tashannah Doller, ; Gide Ng, ; Nathan Riley Sy, 244311
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

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.create_employee, name='create_employee'),
    path('employees/update/<str:pk>/', views.update_employee, name='update_employee'),
    path('employees/delete/<str:pk>/', views.delete_employee, name='delete_employee'),
    path('employees/overtime/<str:pk>/', views.add_overtime, name='add_overtime'),
    path('payslips/', views.payslips_view, name='payslips'),
    path('payslips/view/<int:pk>/', views.view_payslip, name='view_payslip'),
]








'''
Reference(s):
- https://docs.djangoproject.com/en/6.0/topics/auth/default/
'''

