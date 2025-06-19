# apps/menu/models.py - ОБНОВЛЕННАЯ ВЕРСИЯ БЕЗ SLUG
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField('Название категории', max_length=100, unique=True)
    # Добавляем новые поля к существующей модели
    description = models.TextField('Описание категории', blank=True)
    image = models.ImageField('Изображение категории', upload_to='category_images/', blank=True, null=True)
    is_active = models.BooleanField('Активна', default=True)
    sort_order = models.PositiveIntegerField('Порядок сортировки', default=0)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Категория меню'
        verbose_name_plural = 'Категории меню'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('menu:category_detail', kwargs={'pk': self.pk})

    def get_dishes_count(self):
        """Количество активных блюд в категории"""
        return self.menu_items.filter(is_available=True).count()

    def get_available_dishes(self):
        """Получить доступные блюда категории"""
        return self.menu_items.filter(is_available=True)


class MenuItem(models.Model):
    name = models.CharField('Название блюда', max_length=100)
    category = models.ForeignKey(Category, related_name='menu_items', on_delete=models.CASCADE,
                                 verbose_name='Категория')
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    image = models.ImageField('Изображение блюда', upload_to='menu_images/', blank=True, null=True)
    is_available = models.BooleanField('В наличии', default=True, help_text='Доступно ли блюдо для заказа')

    # Добавляем новые поля к существующей модели
    preparation_time = models.PositiveIntegerField('Время приготовления (мин)', default=15)
    calories = models.PositiveIntegerField('Калории', blank=True, null=True)
    weight = models.PositiveIntegerField('Вес (г)', blank=True, null=True)
    is_spicy = models.BooleanField('Острое', default=False)
    is_vegetarian = models.BooleanField('Вегетарианское', default=False)
    is_popular = models.BooleanField('Популярное', default=False)
    cost_price = models.DecimalField('Себестоимость', max_digits=10, decimal_places=2, blank=True, null=True)
    sort_order = models.PositiveIntegerField('Порядок сортировки', default=0)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'
        ordering = ['category', 'sort_order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('menu:item_detail', kwargs={'pk': self.pk})

    @property
    def profit_margin(self):
        """Маржа прибыли в процентах"""
        if self.cost_price and self.cost_price > 0:
            return round(((self.price - self.cost_price) / self.price) * 100, 2)
        return None

    @property
    def profit_amount(self):
        """Сумма прибыли"""
        if self.cost_price:
            return self.price - self.cost_price
        return None


# Новая модель для ингредиентов (для будущей интеграции со складом)
class Ingredient(models.Model):
    name = models.CharField('Название ингредиента', max_length=100)
    unit = models.CharField('Единица измерения', max_length=20, default='г')
    cost_per_unit = models.DecimalField('Стоимость за единицу', max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.unit})"


# Связь блюда с ингредиентами (рецепт)
class Recipe(models.Model):
    dish = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField('Количество', max_digits=8, decimal_places=2)
    notes = models.CharField('Примечания', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        unique_together = ['dish', 'ingredient']

    def __str__(self):
        return f"{self.dish.name} - {self.ingredient.name}"

    @property
    def ingredient_cost(self):
        """Стоимость ингредиента для данного блюда"""
        return self.quantity * self.ingredient.cost_per_unit