from django.db import models


class Category(models.Model):
    name = models.CharField('Название категории', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Категория меню'
        verbose_name_plural = 'Категории меню'
        ordering = ['name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name = models.CharField('Название блюда', max_length=100)
    category = models.ForeignKey(Category, related_name='menu_items', on_delete=models.CASCADE,
                                 verbose_name='Категория')
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    image = models.ImageField('Изображение блюда', upload_to='menu_images/', blank=True, null=True)
    is_available = models.BooleanField('В наличии', default=True, help_text='Доступно ли блюдо для заказа')

    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'
        ordering = ['category', 'name']

    def __str__(self):
        return self.name