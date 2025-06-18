from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views import View
from .models import Ingredient, StockItem, Recipe
from .forms import StockItemForm, QuickIngredientForm, RecipeForm
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuItem


class InventoryDashboardView(LoginRequiredMixin, ListView):
    """Главная страница склада с обзором"""
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
        context['total_stock_value'] = StockItem.objects.aggregate(total=Sum('quantity'))['total'] or 0
        return context


class AddStockItemView(LoginRequiredMixin, CreateView):
    """Добавление товара на склад"""
    model = StockItem
    form_class = StockItemForm
    template_name = 'inventory/add_stock_item.html'

    def get_success_url(self):
        return reverse_lazy('inventory:dashboard')

    def form_valid(self, form):
        # Проверяем, есть ли уже такой товар на складе этого ресторана
        existing_item = StockItem.objects.filter(
            ingredient=form.cleaned_data['ingredient'],
            restaurant=form.cleaned_data['restaurant']
        ).first()

        if existing_item:
            # Если есть, увеличиваем количество
            existing_item.quantity += form.cleaned_data['quantity']
            existing_item.save()
            messages.success(
                self.request,
                f'Количество {existing_item.ingredient.name} увеличено на {form.cleaned_data["quantity"]} {existing_item.ingredient.unit}. '
                f'Общее количество: {existing_item.quantity} {existing_item.ingredient.unit}'
            )
            return redirect(self.get_success_url())
        else:
            # Если нет, создаем новый
            messages.success(self.request, 'Товар успешно добавлен на склад!')
            return super().form_valid(form)


class QuickAddIngredientView(LoginRequiredMixin, CreateView):
    """AJAX view для быстрого добавления ингредиента"""
    model = Ingredient
    form_class = QuickIngredientForm
    template_name = 'inventory/quick_add_ingredient.html'

    def form_valid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX запрос
            ingredient = form.save()
            return JsonResponse({
                'success': True,
                'id': ingredient.id,
                'name': str(ingredient)
            })
        else:
            messages.success(self.request, f'Ингредиент "{form.instance.name}" создан!')
            return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
        return super().form_invalid(form)


class StockUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление количества на складе"""
    model = StockItem
    template_name = 'inventory/stock_update.html'
    fields = ['quantity']

    def get_success_url(self):
        messages.success(self.request, 'Количество на складе обновлено!')
        return reverse_lazy('inventory:stock') + f'?restaurant={self.object.restaurant.id}'


class RecipeManagementView(LoginRequiredMixin, ListView):
    """Управление рецептами блюд"""
    model = Recipe
    template_name = 'inventory/recipes.html'
    context_object_name = 'recipes'

    def get_queryset(self):
        return Recipe.objects.select_related('menu_item', 'ingredient').order_by('menu_item__name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Группируем рецепты по блюдам
        recipes_by_item = {}
        for recipe in context['recipes']:
            if recipe.menu_item not in recipes_by_item:
                recipes_by_item[recipe.menu_item] = []
            recipes_by_item[recipe.menu_item].append(recipe)
        context['recipes_by_item'] = recipes_by_item
        context['menu_items_without_recipes'] = MenuItem.objects.filter(recipe_items__isnull=True)
        return context


class RecipeCreateView(LoginRequiredMixin, CreateView):
    """Создание рецепта"""
    model = Recipe
    form_class = RecipeForm
    template_name = 'inventory/recipe_form.html'
    success_url = reverse_lazy('inventory:recipes')

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Рецепт для {form.instance.menu_item.name} создан!'
        )
        return super().form_valid(form)


class IngredientListView(LoginRequiredMixin, ListView):
    """Список всех ингредиентов"""
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
    """Создание нового ингредиента"""
    model = Ingredient
    template_name = 'inventory/ingredient_form.html'
    fields = ['name', 'unit']
    success_url = reverse_lazy('inventory:ingredients')

    def form_valid(self, form):
        messages.success(self.request, f'Ингредиент "{form.instance.name}" успешно создан!')
        return super().form_valid(form)

class StockListView(LoginRequiredMixin, ListView):
    """Склад конкретного ресторана"""
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
