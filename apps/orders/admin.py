from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['menu_item'] # Удобнее для поиска блюда
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant', 'status', 'created_at', 'total_price')
    list_filter = ('status', 'restaurant')
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]