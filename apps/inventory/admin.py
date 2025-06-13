from django.contrib import admin
from .models import Ingredient, StockItem, Recipe

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')
    search_fields = ('name',)

@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'restaurant', 'quantity', 'last_updated')
    list_filter = ('restaurant',)
    search_fields = ('ingredient__name',)
    autocomplete_fields = ('ingredient', 'restaurant')

admin.site.register(Recipe)