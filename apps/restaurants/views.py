# apps/restaurants/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Restaurant


# LoginRequiredMixin автоматически перенаправляет неавторизованных пользователей на страницу входа.
# Это must-have для защиты страниц.

class RestaurantListView(LoginRequiredMixin, ListView):
    """
    Отображает список всех ресторанов.
    """
    model = Restaurant  # Какую модель используем
    template_name = 'restaurants/list.html'  # Какой шаблон для этого нужен
    context_object_name = 'restaurants'  # Под каким именем передать список в шаблон


class RestaurantDetailView(LoginRequiredMixin, DetailView):
    """
    Отображает подробную информацию о конкретном ресторане.
    """
    model = Restaurant
    template_name = 'restaurants/detail.html'
    context_object_name = 'restaurant'


class RestaurantCreateView(LoginRequiredMixin, CreateView):
    """
    Форма для создания нового ресторана.
    """
    model = Restaurant
    template_name = 'restaurants/form.html'
    fields = ['name', 'address', 'phone_number', 'image']  # Поля, которые будут в форме

    # Куда перенаправить пользователя после успешного создания ресторана.
    # reverse_lazy - "ленивая" версия reverse, идеально для CBV.
    success_url = reverse_lazy('restaurants:list')