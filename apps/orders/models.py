from django.db import models
from django.conf import settings
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuItem


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Ожидает'
        IN_PROGRESS = 'IN_PROGRESS', 'Готовится'
        COMPLETED = 'COMPLETED', 'Завершен'
        CANCELLED = 'CANCELLED', 'Отменен'

    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT, verbose_name='Ресторан')
    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Создал сотрудник'
    )
    total_price = models.DecimalField('Итоговая сумма', max_digits=10, decimal_places=2, default=0)
    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.PENDING)
    table_number = models.PositiveIntegerField('Номер стола', blank=True, null=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ №{self.id} от {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='Заказ')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT, verbose_name='Блюдо')
    quantity = models.PositiveIntegerField('Количество', default=1)
    price_at_moment = models.DecimalField(
        'Цена на момент заказа',
        max_digits=10,
        decimal_places=2,
        help_text='Цена за единицу на момент создания заказа'
    )

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def get_cost(self):
        return self.price_at_moment * self.quantity

    def __str__(self):
        return f'{self.quantity} x {self.menu_item.name}'