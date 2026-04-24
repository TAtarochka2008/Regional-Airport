from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.utils import timezone
from datetime import datetime, date, timedelta
from django.db.models import Q
from .models import Doctor, Patient, Schedule, Appointment, MedicalRecord
from .forms import (
    CustomUserCreationForm, PatientRegistrationForm, DoctorRegistrationForm,
    ScheduleForm, AppointmentForm, MedicalRecordForm
)
from django.contrib import messages


# Проверка ролей
def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Администратор').exists()


def is_doctor(user):
    return hasattr(user, 'doctor')


def is_patient(user):
    return hasattr(user, 'patient')


def index(request):
    """Главная страница"""
    today = timezone.now().date()
    doctors_count = Doctor.objects.filter(is_active=True).count()

    active_specializations = set(Doctor.objects.filter(is_active=True).values_list('specialization', flat=True).distinct())
    specializations = [
        {'value': value, 'label': label, 'count': Doctor.objects.filter(is_active=True, specialization=value).count()}
        for value, label in Doctor.SPECIALIZATION_CHOICES
        if value in active_specializations
    ]

    context = {
        'doctors_count': doctors_count,
        'today': today,
        'specializations': specializations,
    }

    return render(request, 'airport_app/index.html', context)

from django.contrib.auth import logout as auth_logout

def custom_logout(request):
    auth_logout(request)
    messages.success(request, 'Вы успешно вышли из системы аэропорта.')
    return redirect('index')


def doctor_list(request):
    specialization = request.GET.get('specialization', '')

    doctors = Doctor.objects.filter(is_active=True)

    if specialization:
        doctors = doctors.filter(specialization=specialization)

    active_specializations = set(Doctor.objects.filter(is_active=True).values_list('specialization', flat=True).distinct())
    specializations = [
        {'value': value, 'label': label}
        for value, label in Doctor.SPECIALIZATION_CHOICES
        if value in active_specializations
    ]

    context = {
        'doctors': doctors,
        'specializations': specializations,
        'selected_specialization': specialization,
    }

    return render(request, 'airport_app/doctor_list.html', context)


def doctor_schedule(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id, is_active=True)

    schedules = Schedule.objects.filter(doctor=doctor, is_working=True).order_by('day_of_week', 'start_time')

    days = {}
    for schedule in schedules:
        day_name = schedule.get_day_of_week_display()
        if day_name not in days:
            days[day_name] = []
        days[day_name].append(schedule)

    today = timezone.now().date()
    week_from_now = today + timedelta(days=7)

    available_dates = []
    for i in range(7):
        current_date = today + timedelta(days=i)
        day_of_week = current_date.weekday()
        day_of_week = day_of_week + 1 if day_of_week < 6 else 0

        if Schedule.objects.filter(doctor=doctor, day_of_week=day_of_week, is_working=True).exists():
            available_dates.append(current_date)

    context = {
        'doctor': doctor,
        'days': days,
        'available_dates': available_dates,
    }

    return render(request, 'airport_app/schedule.html', context)


@login_required
def create_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id, is_active=True)

    if not hasattr(request.user, 'patient'):
        messages.error(request, 'Только зарегистрированные пассажиры могут оформлять заявки на обслуживание.')
        return redirect('login')

    patient = request.user.patient

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.doctor = doctor
            appointment.office_number = doctor.office_number

            existing_appointment = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment.appointment_date,
                appointment_time=appointment.appointment_time,
                status__in=['запланирован', 'завершен']
            ).exists()

            if existing_appointment:
                messages.error(request, 'Выбранное время уже занято. Пожалуйста, выберите другое время.')
            else:
                appointment.save()
                messages.success(request, 'Заявка на обслуживание успешно создана!')
                return redirect('my_appointments')
    else:
        initial_data = {
            'doctor': doctor,
        }
        form = AppointmentForm(initial=initial_data)

    today = timezone.now().date()
    available_dates = []

    for i in range(14):  # На 2 недели вперед
        current_date = today + timedelta(days=i)
        day_of_week = current_date.weekday()
        day_of_week = day_of_week + 1 if day_of_week < 6 else 0

        if Schedule.objects.filter(doctor=doctor, day_of_week=day_of_week, is_working=True).exists():
            available_dates.append(current_date)

    context = {
        'form': form,
        'doctor': doctor,
        'patient': patient,
        'available_dates': available_dates,
    }

    return render(request, 'airport_app/appointment.html', context)


@login_required
def my_appointments(request):
    if not hasattr(request.user, 'patient'):
        messages.error(request, 'Эта страница доступна только пассажирам.')
        return redirect('index')

    patient = request.user.patient
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date', 'appointment_time')

    today = timezone.now().date()
    upcoming_appointments = appointments.filter(appointment_date__gte=today, status='запланирован')
    past_appointments = appointments.filter(Q(appointment_date__lt=today) | ~Q(status='запланирован'))

    context = {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'today': today,
    }

    return render(request, 'airport_app/my_appointments.html', context)


@login_required
@user_passes_test(is_doctor)
def doctor_appointments(request):
    doctor = request.user.doctor

    selected_date = request.GET.get('date', '')
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=selected_date
    ).order_by('appointment_time')

    today = timezone.now().date()
    date_options = [today + timedelta(days=i) for i in range(-2, 8)]  # 2 дня назад + 7 дней вперед

    context = {
        'doctor': doctor,
        'appointments': appointments,
        'selected_date': selected_date,
        'date_options': date_options,
        'today': today,
    }

    return render(request, 'airport_app/doctor_appointments.html', context)


@login_required
@user_passes_test(is_admin)
def admin_panel(request):
    doctors_count = Doctor.objects.filter(is_active=True).count()
    patients_count = Patient.objects.filter(attached_to_clinic=True).count()
    today_appointments = Appointment.objects.filter(appointment_date=timezone.now().date()).count()
    schedules_count = Schedule.objects.filter(is_working=True).count()

    recent_appointments = Appointment.objects.all().order_by('-created_at')[:10]

    today = timezone.now().date()
    next_week = today + timedelta(days=7)

    all_doctors = Doctor.objects.filter(is_active=True)
    doctors_without_schedule = []

    for doctor in all_doctors:
        tomorrow = today + timedelta(days=1)
        tomorrow_day_of_week = tomorrow.weekday()
        tomorrow_day_of_week = tomorrow_day_of_week + 1 if tomorrow_day_of_week < 6 else 0

        if not Schedule.objects.filter(doctor=doctor, day_of_week=tomorrow_day_of_week, is_working=True).exists():
            doctors_without_schedule.append(doctor)

    context = {
        'doctors_count': doctors_count,
        'patients_count': patients_count,
        'today_appointments': today_appointments,
        'schedules_count': schedules_count,
        'recent_appointments': recent_appointments,
        'doctors_without_schedule': doctors_without_schedule[:5],  # только первые 5
    }

    return render(request, 'airport_app/admin_panel.html', context)


def register_patient(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        patient_form = PatientRegistrationForm(request.POST)

        if user_form.is_valid() and patient_form.is_valid():
            user = user_form.save()

            patient = patient_form.save(commit=False)
            patient.user = user
            patient.save()

            patient_group, created = Group.objects.get_or_create(name='Пассажиры')
            user.groups.add(patient_group)

            username = user_form.cleaned_data.get('username')
            password = user_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)

            messages.success(request, 'Регистрация пассажира прошла успешно!')
            return redirect('index')
    else:
        user_form = CustomUserCreationForm()
        patient_form = PatientRegistrationForm()

    context = {
        'user_form': user_form,
        'patient_form': patient_form,
    }

    return render(request, 'airport_app/register_patient.html', context)


# Административные функции
@login_required
@user_passes_test(is_admin)
def manage_doctors(request):
    doctors = Doctor.objects.all().order_by('user__last_name')

    context = {
        'doctors': doctors,
    }

    return render(request, 'airport_app/manage_doctors.html', context)


@login_required
@user_passes_test(is_admin)
def manage_schedules(request):
    schedules = Schedule.objects.all().order_by('doctor__user__last_name', 'day_of_week', 'start_time')

    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Расписание смены успешно добавлено!')
            return redirect('manage_schedules')
    else:
        form = ScheduleForm()

    context = {
        'schedules': schedules,
        'form': form,
    }

    return render(request, 'airport_app/manage_schedules.html', context)


@login_required
@user_passes_test(is_admin)
def manage_appointments(request):
    appointments = Appointment.objects.all().order_by('-appointment_date', 'appointment_time')

    status_filter = request.GET.get('status', '')
    doctor_filter = request.GET.get('doctor', '')
    date_filter = request.GET.get('date', '')

    if status_filter:
        appointments = appointments.filter(status=status_filter)

    if doctor_filter:
        appointments = appointments.filter(doctor_id=doctor_filter)

    if date_filter:
        appointments = appointments.filter(appointment_date=date_filter)

    doctors = Doctor.objects.filter(is_active=True)

    context = {
        'appointments': appointments,
        'doctors': doctors,
        'status_filter': status_filter,
        'doctor_filter': doctor_filter,
        'date_filter': date_filter,
    }

    return render(request, 'airport_app/manage_appointments.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user.patient)

    if appointment.status == 'запланирован':
        appointment.status = 'отменен'
        appointment.save()
        messages.success(request, 'Заявка успешно отменена.')

    return redirect('my_appointments')


@login_required
@user_passes_test(is_doctor)
def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor)

    if appointment.status == 'запланирован':
        appointment.status = 'завершен'
        appointment.save()
        messages.success(request, 'Обслуживание отмечено как завершенное.')

    return redirect('doctor_appointments')


@login_required
@user_passes_test(is_doctor)
def no_show_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor)

    if appointment.status == 'запланирован':
        appointment.status = 'пассажир не явился'
        appointment.save()
        messages.warning(request, 'Пассажир отмечен как не явившийся.')

    return redirect('doctor_appointments')
