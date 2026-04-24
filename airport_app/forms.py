from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Doctor, Patient, Schedule, Appointment, MedicalRecord
from django.core.exceptions import ValidationError
import datetime


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['birth_date', 'address', 'phone_number', 'insurance_number']
        labels = {
            'birth_date': 'Дата рождения',
            'address': 'Адрес проживания',
            'phone_number': 'Телефон',
            'insurance_number': 'Номер документа пассажира',
        }
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class DoctorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialization', 'qualification', 'experience', 'office_number', 'phone_number']
        labels = {
            'specialization': 'Служба аэропорта',
            'qualification': 'Должность / квалификация',
            'experience': 'Стаж работы',
            'office_number': 'Стойка / зона',
            'phone_number': 'Служебный телефон',
        }


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['doctor', 'day_of_week', 'start_time', 'end_time', 'office_number', 'is_working']
        labels = {
            'doctor': 'Сотрудник',
            'day_of_week': 'День недели',
            'start_time': 'Начало смены',
            'end_time': 'Конец смены',
            'office_number': 'Стойка / зона',
            'is_working': 'Рабочая смена',
        }
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'id': 'id_start_time'  # Добавьте id
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'id': 'id_end_time'  # Добавьте id
            }),
            'office_number': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_office_number'  # Добавьте id
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.filter(is_active=True)
        self.fields['doctor'].label_from_instance = lambda \
            obj: f"{obj.user.get_full_name()} - {obj.get_specialization_display()}"


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'reason']
        labels = {
            'doctor': 'Служба аэропорта',
            'appointment_date': 'Дата обслуживания',
            'appointment_time': 'Время обслуживания',
            'reason': 'Номер рейса, направление или комментарий',
        }
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('appointment_date')

        if appointment_date and appointment_date < datetime.date.today():
            raise ValidationError("Нельзя оформить заявку на прошедшую дату")

        return cleaned_data


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'prescription', 'notes']
        labels = {
            'diagnosis': 'Итог обращения',
            'prescription': 'Назначенные действия',
            'notes': 'Примечания',
        }
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 4}),
            'prescription': forms.Textarea(attrs={'rows': 4}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
