# apps/analytics/views.py
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Count, Sum, Avg
from datetime import datetime, timedelta
from django.utils import timezone

from apps.restaurants.models import Restaurant
from apps.menu.models import MenuItem
from apps.orders.models import Order, OrderItem
from apps.inventory.models import StockItem
from apps.accounts.models import CustomUser


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Главный дашборд с красивой статистикой
    """
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Базовая статистика
        context['total_restaurants'] = Restaurant.objects.count()
        context['total_menu_items'] = MenuItem.objects.count()
        context['total_users'] = CustomUser.objects.count()
        context['total_orders'] = Order.objects.count()

        # Статистика заказов за последние 30 дней
        last_30_days = timezone.now() - timedelta(days=30)
        recent_orders = Order.objects.filter(created_at__gte=last_30_days)

        context['recent_orders_count'] = recent_orders.count()
        context['recent_revenue'] = recent_orders.aggregate(
            total=Sum('total_price')
        )['total'] or 0

        # Топ филиалов по заказам
        context['top_restaurants'] = Restaurant.objects.annotate(
            orders_count=Count('order')
        ).order_by('-orders_count')[:5]

        # Последние заказы
        context['recent_orders'] = Order.objects.select_related(
            'restaurant', 'created_by'
        ).order_by('-created_at')[:5]

        # Статистика по статусам заказов
        context['orders_by_status'] = Order.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')

        # Популярные блюда
        context['popular_items'] = MenuItem.objects.annotate(
            order_count=Count('orderitem')
        ).order_by('-order_count')[:5]

        return context