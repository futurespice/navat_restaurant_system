# apps/analytics/views.py
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import JsonResponse
import json

from apps.restaurants.models import Restaurant
from apps.menu.models import MenuItem, Category
from apps.orders.models import Order, OrderItem
from apps.inventory.models import StockItem
from apps.accounts.models import CustomUser


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Улучшенный главный дашборд с интерактивной аналитикой
    """
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем даты для фильтрации
        today = timezone.now().date()
        last_7_days = today - timedelta(days=7)
        last_30_days = today - timedelta(days=30)

        # === ОСНОВНЫЕ МЕТРИКИ ===
        context.update({
            'total_restaurants': Restaurant.objects.count(),
            'total_menu_items': MenuItem.objects.filter(is_available=True).count(),
            'total_users': CustomUser.objects.count(),
            'total_orders': Order.objects.count(),
            'total_categories': Category.objects.filter(is_active=True).count(),
        })

        # === ФИНАНСОВАЯ СТАТИСТИКА ===
        # За сегодня
        today_orders = Order.objects.filter(created_at__date=today)
        context['today_orders'] = today_orders.count()
        context['today_revenue'] = today_orders.aggregate(
            total=Sum('total_price')
        )['total'] or 0

        # За последние 7 дней
        week_orders = Order.objects.filter(created_at__date__gte=last_7_days)
        context['week_orders'] = week_orders.count()
        context['week_revenue'] = week_orders.aggregate(
            total=Sum('total_price')
        )['total'] or 0

        # За последние 30 дней
        month_orders = Order.objects.filter(created_at__date__gte=last_30_days)
        context['month_orders'] = month_orders.count()
        context['month_revenue'] = month_orders.aggregate(
            total=Sum('total_price')
        )['total'] or 0

        # === СРАВНЕНИЕ С ПРЕДЫДУЩИМ ПЕРИОДОМ ===
        # Предыдущая неделя
        prev_week_start = last_7_days - timedelta(days=7)
        prev_week_orders = Order.objects.filter(
            created_at__date__gte=prev_week_start,
            created_at__date__lt=last_7_days
        )
        prev_week_revenue = prev_week_orders.aggregate(
            total=Sum('total_price')
        )['total'] or 0

        # Рост в процентах
        if prev_week_revenue > 0:
            revenue_growth = ((context['week_revenue'] - prev_week_revenue) / prev_week_revenue) * 100
        else:
            revenue_growth = 100 if context['week_revenue'] > 0 else 0

        context['revenue_growth'] = round(revenue_growth, 1)

        # === СТАТИСТИКА ПО ФИЛИАЛАМ ===
        branches_stats = Restaurant.objects.annotate(
            orders_count=Count('order'),
            revenue=Sum('order__total_price'),
            avg_order_value=Avg('order__total_price')
        ).order_by('-revenue')

        context['top_restaurants'] = branches_stats[:5]
        context['total_revenue'] = sum(r.revenue or 0 for r in branches_stats)

        # === ПОПУЛЯРНЫЕ БЛЮДА ===
        popular_dishes = MenuItem.objects.annotate(
            order_count=Count('orderitem'),
            total_revenue=Sum(F('orderitem__quantity') * F('orderitem__price_at_moment'))
        ).filter(order_count__gt=0).order_by('-order_count')[:10]

        context['popular_dishes'] = popular_dishes

        # === СТАТИСТИКА ПО СТАТУСАМ ЗАКАЗОВ ===
        orders_by_status = Order.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')

        context['orders_by_status'] = list(orders_by_status)

        # === ПОСЛЕДНИЕ ЗАКАЗЫ ===
        context['recent_orders'] = Order.objects.select_related(
            'restaurant', 'created_by'
        ).prefetch_related('items__menu_item').order_by('-created_at')[:8]

        # === СТАТИСТИКА ПО КАТЕГОРИЯМ ===
        categories_stats = Category.objects.annotate(
            dishes_count=Count('menu_items', filter=Q(menu_items__is_available=True)),
            orders_count=Count('menu_items__orderitem')
        ).filter(is_active=True).order_by('-orders_count')

        context['categories_stats'] = categories_stats[:5]

        # === ДАННЫЕ ДЛЯ ГРАФИКОВ (JSON) ===
        # График продаж за последние 7 дней
        daily_sales = Order.objects.filter(
            created_at__date__gte=last_7_days
        ).values('created_at__date').annotate(
            orders=Count('id'),
            revenue=Sum('total_price')
        ).order_by('created_at__date')

        context['daily_sales_json'] = json.dumps([
            {
                'date': item['created_at__date'].strftime('%Y-%m-%d'),
                'orders': item['orders'],
                'revenue': float(item['revenue'] or 0)
            }
            for item in daily_sales
        ])

        # Данные для круговой диаграммы статусов заказов
        context['status_chart_json'] = json.dumps([
            {
                'status': self.get_status_display(item['status']),
                'count': item['count']
            }
            for item in orders_by_status
        ])

        return context

    def get_status_display(self, status):
        """Получить читаемое название статуса"""
        status_map = {
            'PENDING': 'Ожидает',
            'IN_PROGRESS': 'Готовится',
            'COMPLETED': 'Завершен',
            'CANCELLED': 'Отменен'
        }
        return status_map.get(status, status)


class AnalyticsAPIView(LoginRequiredMixin, TemplateView):
    """API для получения данных аналитики через AJAX"""

    def get(self, request, *args, **kwargs):
        period = request.GET.get('period', '7')  # дни
        chart_type = request.GET.get('chart', 'sales')

        try:
            days = int(period)
        except:
            days = 7

        start_date = timezone.now().date() - timedelta(days=days)

        if chart_type == 'sales':
            data = self.get_sales_data(start_date)
        elif chart_type == 'popular_dishes':
            data = self.get_popular_dishes_data(start_date)
        elif chart_type == 'branches':
            data = self.get_branches_data(start_date)
        else:
            data = {'error': 'Unknown chart type'}

        return JsonResponse(data)

    def get_sales_data(self, start_date):
        """Данные продаж по дням"""
        daily_sales = Order.objects.filter(
            created_at__date__gte=start_date
        ).extra(
            select={'date': 'date(created_at)'}
        ).values('date').annotate(
            orders=Count('id'),
            revenue=Sum('total_price')
        ).order_by('date')

        return {
            'labels': [item['date'].strftime('%d.%m') for item in daily_sales],
            'orders': [item['orders'] for item in daily_sales],
            'revenue': [float(item['revenue'] or 0) for item in daily_sales]
        }

    def get_popular_dishes_data(self, start_date):
        """Данные по популярным блюдам"""
        popular = MenuItem.objects.annotate(
            order_count=Count(
                'orderitem',
                filter=Q(orderitem__order__created_at__date__gte=start_date)
            )
        ).filter(order_count__gt=0).order_by('-order_count')[:10]

        return {
            'labels': [dish.name for dish in popular],
            'data': [dish.order_count for dish in popular]
        }

    def get_branches_data(self, start_date):
        """Данные по филиалам"""
        branches = Restaurant.objects.annotate(
            revenue=Sum(
                'order__total_price',
                filter=Q(order__created_at__date__gte=start_date)
            )
        ).filter(revenue__gt=0).order_by('-revenue')[:8]

        return {
            'labels': [branch.name for branch in branches],
            'data': [float(branch.revenue or 0) for branch in branches]
        }


class ReportsView(LoginRequiredMixin, TemplateView):
    """Главная страница отчетов"""
    template_name = 'analytics/reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Доступные типы отчетов
        context['report_types'] = [
            {
                'name': 'Отчет по продажам',
                'description': 'Детальная аналитика продаж по периодам',
                'icon': 'fa-chart-bar',
                'url': 'analytics:sales_report',
                'color': 'primary'
            },
            {
                'name': 'Отчет по меню',
                'description': 'Популярность блюд и категорий',
                'icon': 'fa-utensils',
                'url': 'analytics:menu_report',
                'color': 'success'
            },
            {
                'name': 'Отчет по филиалам',
                'description': 'Сравнительная аналитика филиалов',
                'icon': 'fa-store',
                'url': 'analytics:branches_report',
                'color': 'warning'
            },
        ]

        return context


class SalesReportView(LoginRequiredMixin, TemplateView):
    """Детальный отчет по продажам"""
    template_name = 'analytics/sales_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем параметры фильтрации
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        branch_id = self.request.GET.get('branch')

        # Базовый queryset заказов
        orders = Order.objects.all()

        if start_date:
            orders = orders.filter(created_at__date__gte=start_date)
        if end_date:
            orders = orders.filter(created_at__date__lte=end_date)
        if branch_id:
            orders = orders.filter(restaurant_id=branch_id)

        # Статистика
        context.update({
            'total_orders': orders.count(),
            'total_revenue': orders.aggregate(Sum('total_price'))['total_price'] or 0,
            'avg_order_value': orders.aggregate(Avg('total_price'))['total_price'] or 0,
            'branches': Restaurant.objects.all(),
            'selected_branch': branch_id,
            'start_date': start_date,
            'end_date': end_date,
        })

        # Продажи по дням
        daily_sales = orders.extra(
            select={'date': 'date(created_at)'}
        ).values('date').annotate(
            orders_count=Count('id'),
            revenue=Sum('total_price')
        ).order_by('date')

        context['daily_sales'] = daily_sales

        return context


class MenuReportView(LoginRequiredMixin, TemplateView):
    """Отчет по меню и популярности блюд"""
    template_name = 'analytics/menu_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Популярные блюда
        popular_dishes = MenuItem.objects.annotate(
            order_count=Count('orderitem'),
            total_revenue=Sum(F('orderitem__quantity') * F('orderitem__price_at_moment'))
        ).filter(order_count__gt=0).order_by('-order_count')

        context['popular_dishes'] = popular_dishes

        # Статистика по категориям
        category_stats = Category.objects.annotate(
            dishes_count=Count('menu_items'),
            orders_count=Count('menu_items__orderitem'),
            revenue=Sum(F('menu_items__orderitem__quantity') * F('menu_items__orderitem__price_at_moment'))
        ).filter(is_active=True).order_by('-revenue')

        context['category_stats'] = category_stats

        # Неиспользуемые блюда
        unused_dishes = MenuItem.objects.annotate(
            order_count=Count('orderitem')
        ).filter(order_count=0, is_available=True)

        context['unused_dishes'] = unused_dishes

        return context


class BranchesReportView(LoginRequiredMixin, TemplateView):
    """Отчет по филиалам"""
    template_name = 'analytics/branches_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Статистика по филиалам
        branches_stats = Restaurant.objects.annotate(
            orders_count=Count('order'),
            revenue=Sum('order__total_price'),
            avg_order_value=Avg('order__total_price'),
            employees_count=Count('employees', distinct=True)
        ).order_by('-revenue')

        context['branches_stats'] = branches_stats

        # Общая статистика
        total_revenue = sum(b.revenue or 0 for b in branches_stats)
        context['total_revenue'] = total_revenue

        return context