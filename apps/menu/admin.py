# apps/menu/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, MenuItem, Ingredient, Recipe


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_dishes_count', 'sort_order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('sort_order', 'is_active')
    ordering = ('sort_order', 'name')

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description')
        }),
        ('Внешний вид', {
            'fields': ('image',)
        }),
        ('Настройки', {
            'fields': ('sort_order', 'is_active')
        }),
    )

    def get_dishes_count(self, obj):
        count = obj.get_dishes_count()
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if count > 0 else 'red',
            count
        )

    get_dishes_count.short_description = 'Количество блюд'
    get_dishes_count.admin_order_field = 'menu_items__count'


class RecipeInline(admin.TabularInline):
    model = Recipe
    extra = 1
    fields = ('ingredient', 'quantity', 'notes')


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'price', 'cost_price', 'get_profit_margin',
        'is_available', 'is_popular', 'preparation_time'
    )
    list_filter = (
        'category', 'is_available', 'is_spicy', 'is_vegetarian',
        'is_popular', 'created_at'
    )
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_available', 'is_popular')
    ordering = ('category', 'sort_order', 'name')
    inlines = [RecipeInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'category', 'description')
        }),
        ('Ценообразование', {
            'fields': ('price', 'cost_price')
        }),
        ('Характеристики', {
            'fields': ('preparation_time', 'weight', 'calories')
        }),
        ('Свойства', {
            'fields': ('is_available', 'is_spicy', 'is_vegetarian', 'is_popular')
        }),
        ('Медиа', {
            'fields': ('image',)
        }),
        ('Система', {
            'fields': ('sort_order',),
            'classes': ('collapse',)
        }),
    )

    def get_profit_margin(self, obj):
        margin = obj.profit_margin
        if margin is not None:
            color = 'green' if margin > 50 else 'orange' if margin > 30 else 'red'
            return format_html(
                '<span style="color: {};">{:.1f}%</span>',
                color,
                margin
            )
        return '-'

    get_profit_margin.short_description = 'Маржа'
    get_profit_margin.admin_order_field = 'price'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'cost_per_unit')
    list_filter = ('unit',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('dish', 'ingredient', 'quantity', 'ingredient_cost')
    list_filter = ('dish__category', 'ingredient')
    search_fields = ('dish__name', 'ingredient__name')
    ordering = ('dish__name', 'ingredient__name')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('dish', 'ingredient')