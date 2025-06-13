from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Администратор системы'
        MANAGER = 'MANAGER', 'Менеджер филиала'
        STAFF = 'STAFF', 'Рядовой сотрудник'

    email = models.EmailField('адрес электронной почты', unique=True)
    role = models.CharField('Роль', max_length=50, choices=Role.choices, default=Role.STAFF)

    # Мы будем использовать email для входа в систему
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


