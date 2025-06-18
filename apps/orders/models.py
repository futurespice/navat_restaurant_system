from django.db import models, transaction
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuItem
from apps.inventory.models import StockItem

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
    ingredients_processed = models.BooleanField('Ингредиенты списаны', default=False)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ №{self.id} от {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def calculate_total(self):
        """Автоматический расчет общей суммы заказа"""
        total = sum(item.get_cost() for item in self.items.all())
        self.total_price = total
        return total

    def process_ingredients(self):
        """Списание ингредиентов со склада при заказе"""
        if self.ingredients_processed:
            return {"success": True, "message": "Ингредиенты уже были списаны"}

        if self.status not in [self.Status.IN_PROGRESS, self.Status.COMPLETED]:
            return {"success": False, "message": "Заказ должен быть в процессе или завершен"}

        warnings = []

        try:
            with transaction.atomic():
                for order_item in self.items.select_related('menu_item'):
                    # Получаем рецепт блюда
                    recipes = order_item.menu_item.recipe_items.select_related('ingredient')

                    for recipe in recipes:
                        # Находим запас на складе этого ресторана
                        try:
                            stock_item = StockItem.objects.get(
                                ingredient=recipe.ingredient,
                                restaurant=self.restaurant
                            )

                            # Рассчитываем нужное количество
                            needed_amount = recipe.quantity * order_item.quantity

                            if stock_item.quantity >= needed_amount:
                                # Списываем со склада
                                stock_item.quantity -= needed_amount
                                stock_item.save()
                            else:
                                warnings.append(
                                    f"Недостаточно {recipe.ingredient.name}: "
                                    f"нужно {needed_amount} {recipe.ingredient.unit}, "
                                    f"доступно {stock_item.quantity} {recipe.ingredient.unit}"
                                )
                                # Списываем все что есть
                                stock_item.quantity = 0
                                stock_item.save()

                        except StockItem.DoesNotExist:
                            warnings.append(
                                f"Ингредиент {recipe.ingredient.name} отсутствует на складе"
                            )

                # Отмечаем что ингредиенты обработаны
                self.ingredients_processed = True
                self.save()

                return {
                    "success": True,
                    "message": "Ингредиенты успешно списаны",
                    "warnings": warnings
                }

        except Exception as e:
            return {"success": False, "message": f"Ошибка при списании: {str(e)}"}

    def save(self, *args, **kwargs):
        # Автоматический расчет суммы при сохранении
        if self.pk:  # Если заказ уже существует
            self.calculate_total()
        super().save(*args, **kwargs)

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

    def save(self, *args, **kwargs):
        # Автоматически сохраняем текущую цену при создании
        if not self.price_at_moment:
            self.price_at_moment = self.menu_item.price
        super().save(*args, **kwargs)

        # Пересчитываем общую сумму заказа
        if self.order_id:
            self.order.calculate_total()
            self.order.save()

# Signal для автоматического списания ингредиентов
@receiver(post_save, sender=Order)
def process_order_ingredients(sender, instance, created, **kwargs):
    """Signal для автоматического списания ингредиентов при изменении статуса"""
    if not created and instance.status == Order.Status.IN_PROGRESS and not instance.ingredients_processed:
        # Автоматически списываем ингредиенты когда заказ переходит в статус "Готовится"
        result = instance.process_ingredients()

        # Можно добавить логирование или уведомления
        if not result["success"]:
            print(f"Ошибка при списании ингредиентов для заказа {instance.id}: {result['message']}")