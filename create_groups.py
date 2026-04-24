import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airport_system.settings')
django.setup()

from django.contrib.auth.models import Group

groups = ['Администратор', 'Сотрудники аэропорта', 'Пассажиры']

for group_name in groups:
    group, created = Group.objects.get_or_create(name=group_name)
    if created:
        print(f'Группа "{group_name}" создана')
    else:
        print(f'Группа "{group_name}" уже существует')
