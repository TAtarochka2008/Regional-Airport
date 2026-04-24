from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Общедоступные страницы
    path('', views.index, name='index'),
    path('services/', views.doctor_list, name='doctor_list'),
    path('service/<int:doctor_id>/', views.doctor_schedule, name='doctor_schedule'),

    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='airport_app/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/passenger/', views.register_patient, name='register_patient'),

    # Пассажиры
    path('request/create/<int:doctor_id>/', views.create_appointment, name='create_appointment'),
    path('my-requests/', views.my_appointments, name='my_appointments'),
    path('request/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),

    # Сотрудники аэропорта
    path('employee/requests/', views.doctor_appointments, name='doctor_appointments'),
    path('request/complete/<int:appointment_id>/', views.complete_appointment, name='complete_appointment'),
    path('request/no-show/<int:appointment_id>/', views.no_show_appointment, name='no_show_appointment'),

    # Администратор
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('manage-employees/', views.manage_doctors, name='manage_doctors'),
    path('manage-shifts/', views.manage_schedules, name='manage_schedules'),
    path('manage-requests/', views.manage_appointments, name='manage_appointments'),
]
