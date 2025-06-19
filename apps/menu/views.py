# apps/menu/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.http import JsonResponse

from .models import MenuItem, Category
from .forms import CategoryForm, MenuItemForm, CategoryFilterForm


class MenuListView(LoginRequiredMixin, ListView):
    """
    Улучшенный список меню с фильтрацией и поиском
    """
    model = Category
    template_name = 'menu/list.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем параметры фильтрации
        search_query = self.request.GET.get('search', '')
        category_filter = self.request.GET.get('category', '')
        availability_filter = self.request.GET.get('availability', '')

        # Базовый запрос категорий с блюдами
        categories = Category.objects.filter(is_active=True).prefetch_related('menu_items')

        # Если есть поиск или фильтры, фильтруем блюда
        if search_query or category_filter or availability_filter:
            dishes_query = MenuItem.objects.all()

            if search_query:
                dishes_query = dishes_query.filter(
                    Q(name__icontains=search_query) |
                    Q(description__icontains=search_query)
                )

            if category_filter:
                dishes_query = dishes_query.filter(category_id=category_filter)

            if availability_filter == 'available':
                dishes_query = dishes_query.filter(is_available=True)
            elif availability_filter == 'unavailable':
                dishes_query = dishes_query.filter(is_available=False)

            context['filtered_dishes'] = dishes_query
            context['is_filtered'] = True
        else:
            context['is_filtered'] = False

        # Добавляем данные для фильтров
        context['all_categories'] = Category.objects.filter(is_active=True)
        context['search_query'] = search_query
        context['category_filter'] = category_filter
        context['availability_filter'] = availability_filter
        context['categories'] = categories

        return context


class MenuItemCreateView(LoginRequiredMixin, CreateView):
    """
    Улучшенная форма создания блюда
    """
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'menu/form.html'
    success_url = reverse_lazy('menu:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Создание нового блюда'
        context['categories'] = Category.objects.filter(is_active=True)
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Блюдо "{form.instance.name}" успешно создано!')
        return super().form_valid(form)


class MenuItemUpdateView(LoginRequiredMixin, UpdateView):
    """
    Улучшенная форма редактирования блюда
    """
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'menu/form.html'
    success_url = reverse_lazy('menu:list')
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Редактирование блюда "{self.object.name}"'
        context['categories'] = Category.objects.filter(is_active=True)
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Блюдо "{form.instance.name}" успешно обновлено!')
        return super().form_valid(form)


class MenuItemDeleteView(LoginRequiredMixin, DeleteView):
    """
    Улучшенное удаление блюда с проверками
    """
    model = MenuItem
    template_name = 'menu/delete_confirm.html'
    success_url = reverse_lazy('menu:list')
    context_object_name = 'item'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        dish_name = self.object.name
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, f'Блюдо "{dish_name}" успешно удалено!')
        return redirect(success_url)


# НОВЫЕ VIEWS ДЛЯ УПРАВЛЕНИЯ КАТЕГОРИЯМИ
class CategoryListView(LoginRequiredMixin, ListView):
    """
    Список категорий для управления
    """
    model = Category
    template_name = 'menu/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(is_active=True).order_by('sort_order', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = context['categories']

        # Подсчитываем статистику
        total_dishes = sum(cat.get_dishes_count() for cat in categories)
        categories_with_images = sum(1 for cat in categories if cat.image)
        empty_categories = sum(1 for cat in categories if cat.get_dishes_count() == 0)

        context.update({
            'total_dishes': total_dishes,
            'categories_with_images': categories_with_images,
            'empty_categories': empty_categories,
        })

        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """
    Создание новой категории
    """
    model = Category
    form_class = CategoryForm
    template_name = 'menu/category_form.html'
    success_url = reverse_lazy('menu:category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Создание новой категории'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Категория "{form.instance.name}" успешно создана!')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """
    Редактирование категории
    """
    model = Category
    form_class = CategoryForm
    template_name = 'menu/category_form.html'
    success_url = reverse_lazy('menu:category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Редактирование категории "{self.object.name}"'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Категория "{form.instance.name}" успешно обновлена!')
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """
    Удаление категории с проверкой на наличие блюд
    """
    model = Category
    template_name = 'menu/category_delete_confirm.html'
    success_url = reverse_lazy('menu:category_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Проверяем, есть ли блюда в категории
        if self.object.menu_items.exists():
            messages.error(
                request,
                f'Нельзя удалить категорию "{self.object.name}" - в ней есть блюда!'
            )
            return redirect(self.success_url)

        category_name = self.object.name
        self.object.delete()
        messages.success(request, f'Категория "{category_name}" успешно удалена!')
        return redirect(self.success_url)


# AJAX VIEWS ДЛЯ ДИНАМИЧЕСКИХ ОПЕРАЦИЙ

def toggle_dish_availability(request, pk):
    """
    AJAX переключение доступности блюда
    """
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            dish = MenuItem.objects.get(pk=pk)
            dish.is_available = not dish.is_available
            dish.save()

            return JsonResponse({
                'success': True,
                'is_available': dish.is_available,
                'message': f'Блюдо "{dish.name}" {"доступно" if dish.is_available else "недоступно"}'
            })
        except MenuItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Блюдо не найдено'})

    return JsonResponse({'success': False, 'message': 'Недопустимый запрос'})


def get_category_dishes(request, category_id):
    """
    AJAX получение блюд категории
    """
    if request.user.is_authenticated:
        try:
            category = Category.objects.get(pk=category_id)
            dishes = category.menu_items.all().values(
                'id', 'name', 'price', 'is_available', 'image'
            )
            return JsonResponse({
                'success': True,
                'dishes': list(dishes),
                'category_name': category.name
            })
        except Category.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Категория не найдена'})

    return JsonResponse({'success': False, 'message': 'Не авторизован'})