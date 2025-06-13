# apps/inventory/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q

from .models import Ingredient, StockItem, Recipe
from apps.restaurants.models import Restaurant


class InventoryDashboardView(LoginRequiredMixin, ListView):
    """
    Главная страница склада с обзором
    """
    model = StockItem
    template_name = 'inventory/dashboard.html'
    context_object_name = 'stock_items'

    def get_queryset(self):
        return StockItem.objects.select_related('ingredient', 'restaurant').order_by('restaurant', 'ingredient__name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_ingredients'] = Ingredient.objects.count()
        context['restaurants'] = Restaurant.objects.all()
        context['low_stock_items'] = StockItem.objects.filter(quantity__lt=10).select_related('ingredient',
                                                                                              'restaurant')
        return context


class IngredientListView(LoginRequiredMixin, ListView):
    """
    Список всех ингредиентов
    """
    model = Ingredient
    template_name = 'inventory/ingredients.html'
    context_object_name = 'ingredients'
    paginate_by = 20

    def get_queryset(self):
        queryset = Ingredient.objects.all().order_by('name')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(unit__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class IngredientCreateView(LoginRequiredMixin, CreateView):
    """
    Создание нового ингредиента
    """
    model = Ingredient
    template_name = 'inventory/ingredient_form.html'
    fields = ['name', 'unit']
    success_url = reverse_lazy('inventory:ingredients')

    def form_valid(self, form):
        messages.success(self.request, f'Ингредиент "{form.instance.name}" успешно создан!')
        return super().form_valid(form)


class StockListView(LoginRequiredMixin, ListView):
    """
    Склад конкретного ресторана
    """
    model = StockItem
    template_name = 'inventory/stock.html'
    context_object_name = 'stock_items'
    paginate_by = 20

    def get_queryset(self):
        restaurant_id = self.request.GET.get('restaurant')
        queryset = StockItem.objects.select_related('ingredient', 'restaurant').order_by('ingredient__name')

        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurants'] = Restaurant.objects.all()
        context['current_restaurant'] = self.request.GET.get('restaurant', '')
        return context


class StockUpdateView(LoginRequiredMixin, UpdateView):
    """
    Обновление количества на складе
    """
    model = StockItem
    template_name = 'inventory/stock_update.html'
    fields = ['quantity']

    def get_success_url(self):
        messages.success(self.request, 'Количество на складе обновлено!')
        return reverse_lazy('inventory:stock') + f'?restaurant={self.object.restaurant.id}'


class AddStockItemView(LoginRequiredMixin, CreateView):
    """
    Добавление нового товара на склад
    """
    model = StockItem
    template_name = 'inventory/add_stock_item.html'
    fields = ['ingredient', 'restaurant', 'quantity']

    def get_success_url(self):
        messages.success(self.request, 'Товар добавлен на склад!')
        return reverse_lazy('inventory:stock') + f'?restaurant={self.object.restaurant.id}'