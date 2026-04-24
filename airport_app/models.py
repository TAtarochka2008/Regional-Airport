from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Doctor(models.Model):
    SPECIALIZATION_CHOICES = [
        ('регистрация', 'Регистрация пассажиров'),
        ('досмотр', 'Предполетный досмотр'),
        ('багаж', 'Багажная служба'),
        ('информация', 'Информационная стойка'),
        ('посадка', 'Посадка на рейс'),
        ('грузовой терминал', 'Грузовой терминал'),
        ('медпункт', 'Медпункт аэропорта'),
        ('vip-зал', 'VIP-зал'),
        ('транспорт', 'Наземный транспорт'),
        ('авиакасса', 'Авиакасса'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor')
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    qualification = models.CharField(max_length=255)
    experience = models.PositiveIntegerField(help_text="Стаж работы в годах")
    office_number = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_specialization_display()}"

    class Meta:
        verbose_name = "Сотрудник аэропорта"
        verbose_name_plural = "Сотрудники аэропорта"


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    birth_date = models.DateField()
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    insurance_number = models.CharField(max_length=20, unique=True)
    attached_to_clinic = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.insurance_number}"

    class Meta:
        verbose_name = "Пассажир"
        verbose_name_plural = "Пассажиры"


class Schedule(models.Model):
    DAYS_OF_WEEK = [
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
        (0, 'Воскресенье'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    office_number = models.CharField(max_length=10)
    is_working = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.doctor} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

    class Meta:
        verbose_name = "Расписание смены"
        verbose_name_plural = "Расписания смен"
        ordering = ['day_of_week', 'start_time']


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('запланирован', 'Запланирован'),
        ('завершен', 'Завершен'),
        ('отменен', 'Отменен'),
        ('пассажир не явился', 'Пассажир не явился'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    office_number = models.CharField(max_length=10)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='запланирован')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient} -> {self.doctor} - {self.appointment_date} {self.appointment_time}"

    class Meta:
        verbose_name = "Заявка пассажира"
        verbose_name_plural = "Заявки пассажиров"
        ordering = ['-appointment_date', 'appointment_time']


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='medical_records')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='medical_record', null=True,
                                       blank=True)
    diagnosis = models.TextField()
    prescription = models.TextField()
    notes = models.TextField(blank=True)
    record_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Служебная запись: {self.patient} - {self.record_date.date()}"

    class Meta:
        verbose_name = "Служебная запись"
        verbose_name_plural = "Служебные записи"
