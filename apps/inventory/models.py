from django.db import models
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuItem


class Ingredient(models.Model):
    name = models.CharField('Название ингредиента', max_length=100, unique=True)
    unit = models.CharField('Единица измерения', max_length=20, help_text='например: кг, л, шт.')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.unit}'


class StockItem(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='stock_items',
                                   verbose_name='Ресторан')
    quantity = models.DecimalField('Количество', max_digits=10, decimal_places=3, default=0)
    last_updated = models.DateTimeField('Последнее обновление', auto_now=True)

    class Meta:
        unique_together = ('ingredient', 'restaurant')
        verbose_name = 'Позиция на складе'
        verbose_name_plural = 'Склад'

    def __str__(self):
        return f'{self.ingredient.name} на складе {self.restaurant.name}'


class Recipe(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='recipe_items', verbose_name='Блюдо')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент')
    quantity = models.DecimalField('Количество', max_digits=10, decimal_places=3,
                                   help_text='Сколько единиц ингредиента нужно на одну порцию')

    class Meta:
        unique_together = ('menu_item', 'ingredient')
        verbose_name = 'Компонент рецепта'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.quantity} {self.ingredient.unit} для "{self.menu_item.name}"'