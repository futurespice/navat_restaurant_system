from django.db import models

class Restaurant(models.Model):
    name = models.CharField('Название филиала', max_length=100)
    address = models.CharField('Адрес', max_length=255)
    phone_number = models.CharField('Телефон', max_length=20)
    image = models.ImageField('Фотография ресторана', upload_to='restaurants_images/', blank=True, null=True)

    class Meta:
        verbose_name = 'Ресторан'
        verbose_name_plural = 'Рестораны'
        ordering = ['name']

    def __str__(self):
        return self.name