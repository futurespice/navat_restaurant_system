# apps/menu/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import MenuItem, Category


class MenuListView(LoginRequiredMixin, ListView):
    """
    Отображает список всех блюд.
    Мы переопределим get_context_data, чтобы сгруппировать блюда по категориям.
    """
    model = Category
    template_name = 'menu/list.html'
    context_object_name = 'categories'

    # Этот метод позволяет нам передавать в шаблон не только categories,
    # но и любые другие данные.
    def get_context_data(self, **kwargs):
        # Сначала получаем базовый контекст
        context = super().get_context_data(**kwargs)
        # Добавляем в него все блюда, связанные с категориями (для эффективности)
        context['categories'] = Category.objects.prefetch_related('menu_items')
        return context


class MenuItemCreateView(LoginRequiredMixin, CreateView):
    """
    Форма для создания нового блюда.
    """
    model = MenuItem
    template_name = 'menu/form.html'
    fields = ['name', 'category', 'description', 'price', 'image', 'is_available']
    success_url = reverse_lazy('menu:list')

    # Добавляем в контекст заголовок страницы, чтобы использовать один шаблон и для создания, и для редактирования
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Создание нового блюда'
        return context


class MenuItemUpdateView(LoginRequiredMixin, UpdateView):
    """
    Форма для редактирования существующего блюда.
    UpdateView очень похож на CreateView, но он работает с уже существующим объектом.
    """
    model = MenuItem
    template_name = 'menu/form.html'
    fields = ['name', 'category', 'description', 'price', 'image', 'is_available']
    success_url = reverse_lazy('menu:list')
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Редактирование блюда'
        return context


class MenuItemDeleteView(LoginRequiredMixin, DeleteView):
    """
    Страница подтверждения удаления блюда.
    """
    model = MenuItem
    template_name = 'menu/delete_confirm.html'
    success_url = reverse_lazy('menu:list')
    context_object_name = 'item'