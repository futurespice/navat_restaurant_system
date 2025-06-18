from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from django.http import JsonResponse
from .models import Order, OrderItem
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuItem, Category
from .forms import OrderForm


class OrderListView(LoginRequiredMixin, ListView):
    """
    Список всех заказов с красивой фильтрацией
    """
    model = Order
    template_name = 'orders/list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        queryset = Order.objects.select_related('restaurant', 'created_by').order_by('-created_at')

        # Фильтрация по статусу
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Фильтрация по ресторану
        restaurant = self.request.GET.get('restaurant')
        if restaurant:
            queryset = queryset.filter(restaurant_id=restaurant)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurants'] = Restaurant.objects.all()
        context['status_choices'] = Order.Status.choices
        context['current_status'] = self.request.GET.get('status', '')
        context['current_restaurant'] = self.request.GET.get('restaurant', '')
        return context


class AddItemToOrderView(LoginRequiredMixin, View):
    """
    Добавление позиции в заказ
    """

    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        menu_item_id = request.POST.get('menu_item_id')
        quantity = int(request.POST.get('quantity', 1))

        menu_item = get_object_or_404(MenuItem, pk=menu_item_id)

        with transaction.atomic():
            # Проверяем, есть ли уже такая позиция в заказе
            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                menu_item=menu_item,
                defaults={
                    'quantity': quantity,
                    'price_at_moment': menu_item.price
                }
            )

            if not created:
                # Если позиция уже есть, увеличиваем количество
                order_item.quantity += quantity
                order_item.save()

            # Пересчитываем общую стоимость заказа
            total = sum(item.get_cost() for item in order.items.all())
            order.total_price = total
            order.save()

        messages.success(request, f'Добавлено: {menu_item.name} x{quantity}')
        return redirect('orders:detail', pk=order_id)


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование заказа"""
    model = Order
    template_name = 'orders/update.html'
    fields = ['restaurant', 'table_number', 'status']

    def get_success_url(self):
        messages.success(self.request, 'Заказ успешно обновлен!')
        return reverse_lazy('orders:detail', kwargs={'pk': self.object.pk})

class UpdateOrderStatusView(LoginRequiredMixin, UpdateView):
    """
    Обновление статуса заказа
    """
    model = Order
    fields = ['status']
    template_name = 'orders/update_status.html'

    def get_success_url(self):
        messages.success(self.request, 'Статус заказа обновлен!')
        return reverse_lazy('orders:detail', kwargs={'pk': self.object.pk})


class OrderDetailView(LoginRequiredMixin, DetailView):
    """Подробная информация о заказе с возможностью списания ингредиентов"""
    model = Order
    template_name = 'orders/detail.html'
    context_object_name = 'order'

    def get_object(self):
        return get_object_or_404(
            Order.objects.select_related('restaurant', 'created_by').prefetch_related('items__menu_item'),
            pk=self.kwargs['pk']
        )

    def post(self, request, *args, **kwargs):
        """Обработка действий с заказом"""
        order = self.get_object()
        action = request.POST.get('action')

        if action == 'process_ingredients':
            result = order.process_ingredients()
            if result["success"]:
                messages.success(request, result["message"])
                if result.get("warnings"):
                    for warning in result["warnings"]:
                        messages.warning(request, warning)
            else:
                messages.error(request, result["message"])

        elif action == 'update_status':
            new_status = request.POST.get('status')
            if new_status in dict(Order.Status.choices):
                old_status = order.status
                order.status = new_status
                order.save()
                messages.success(request,
                                 f'Статус заказа изменен с "{order.get_status_display()}" на "{dict(Order.Status.choices)[new_status]}"')

        return redirect('orders:detail', pk=order.pk)


class ProcessIngredientsView(LoginRequiredMixin, View):
    """AJAX view для списания ингредиентов"""

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        result = order.process_ingredients()

        return JsonResponse(result)


class OrderReceiptView(LoginRequiredMixin, DetailView):
    """Просмотр чека заказа"""
    model = Order
    template_name = 'orders/receipt.html'
    context_object_name = 'order'

    def get_object(self):
        return get_object_or_404(
            Order.objects.select_related('restaurant', 'created_by').prefetch_related('items__menu_item'),
            pk=self.kwargs['pk']
        )


class OrderCreateView(LoginRequiredMixin, CreateView):
    """Создание нового заказа"""
    model = Order
    form_class = OrderForm
    template_name = 'orders/create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Заказ успешно создан!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('orders:detail', kwargs={'pk': self.object.pk})


