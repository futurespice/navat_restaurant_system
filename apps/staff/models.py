from django.db import models
from django.conf import settings
from apps.restaurants.models import Restaurant

class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Учетная запись'
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name='Филиал'
    )
    position = models.CharField('Должность', max_length=100) # Например: Официант, Повар, Хостес
    hire_date = models.DateField('Дата найма', auto_now_add=True)
    photo = models.ImageField('Фото', upload_to='staff_images/', blank=True, null=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.position})"