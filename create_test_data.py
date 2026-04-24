import os
import django
from datetime import date, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airport_system.settings')
django.setup()

from django.contrib.auth.models import User, Group
from airport_app.models import Doctor, Patient, Schedule, Appointment


# Создание тестовых пользователей
def create_test_data():
    # Создаем сотрудников аэропорта
    specializations = ['регистрация', 'досмотр', 'багаж', 'информация', 'посадка']
    employees = [
        ('Кирилл', 'Волков'),
        ('Анна', 'Орлова'),
        ('Дмитрий', 'Соколов'),
        ('Елена', 'Морозова'),
        ('Роман', 'Лебедев'),
    ]

    for i, (first_name, last_name) in enumerate(employees, start=1):
        user, created = User.objects.get_or_create(
            username=f'employee{i}',
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': f'employee{i}@airport.ru'
            }
        )
        if not created:
            user.first_name = first_name
            user.last_name = last_name
            user.email = f'employee{i}@airport.ru'
            user.save()

        if created:
            user.set_password('password123')
            user.save()

            doctor = Doctor.objects.create(
                user=user,
                specialization=random.choice(specializations),
                qualification='Старший специалист смены',
                experience=random.randint(5, 25),
                office_number=f'B{i}',
                phone_number=f'+7(999)123-45-{i}'
            )

            # Добавляем сотрудника в группу
            doctor_group, _ = Group.objects.get_or_create(name='Сотрудники аэропорта')
            user.groups.add(doctor_group)

            print(f'Создан сотрудник аэропорта: {doctor}')

    # Создаем пассажиров
    passengers = [
        ('Алиса', 'Никитина'),
        ('Максим', 'Федоров'),
        ('Полина', 'Ильина'),
        ('Артем', 'Калинин'),
        ('Виктория', 'Егорова'),
        ('Никита', 'Зайцев'),
        ('Софья', 'Павлова'),
        ('Игорь', 'Киселев'),
        ('Дарья', 'Тихонова'),
        ('Михаил', 'Беляев'),
    ]

    for i, (first_name, last_name) in enumerate(passengers, start=1):
        user, created = User.objects.get_or_create(
            username=f'passenger{i}',
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': f'passenger{i}@mail.ru'
            }
        )
        if not created:
            user.first_name = first_name
            user.last_name = last_name
            user.email = f'passenger{i}@mail.ru'
            user.save()

        if created:
            user.set_password('password123')
            user.save()

            patient = Patient.objects.create(
                user=user,
                birth_date=date(1980, 1, 1) + timedelta(days=i * 365),
                address=f'г. Томск, ул. Примерная, д.{i}',
                phone_number=f'+7(999)987-65-{i}',
                insurance_number=f'PASS-{i:06d}'
            )

            # Добавляем пассажира в группу
            patient_group, _ = Group.objects.get_or_create(name='Пассажиры')
            user.groups.add(patient_group)

            print(f'Создан пассажир: {patient}')

    print("Тестовые данные созданы успешно!")


if __name__ == '__main__':
    create_test_data()
