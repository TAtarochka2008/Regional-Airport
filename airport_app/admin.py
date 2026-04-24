from django.contrib import admin
from .models import Doctor, Patient, Schedule, Appointment, MedicalRecord

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'office_number', 'phone_number', 'is_active']
    list_filter = ['specialization', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'specialization']

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['user', 'insurance_number', 'birth_date', 'attached_to_clinic']
    search_fields = ['user__first_name', 'user__last_name', 'insurance_number']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time', 'office_number', 'is_working']
    list_filter = ['day_of_week', 'is_working', 'doctor__specialization']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'appointment_time', 'status', 'office_number']
    list_filter = ['status', 'appointment_date', 'doctor__specialization']
    date_hierarchy = 'appointment_date'

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'record_date']
    search_fields = ['patient__user__first_name', 'diagnosis']