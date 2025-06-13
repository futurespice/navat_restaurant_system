# apps/staff/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q

from .models import Employee
from apps.accounts.models import CustomUser
from apps.restaurants.models import Restaurant


class StaffListView(LoginRequiredMixin, ListView):
    """
    Список всех сотрудников
    """
    model = Employee
    template_name = 'staff/list.html'
    context_object_name = 'employees'
    paginate_by = 20

    def get_queryset(self):
        queryset = Employee.objects.select_related('user', 'restaurant').order_by('user__last_name', 'user__first_name')

        # Фильтрация по ресторану
        restaurant = self.request.GET.get('restaurant')
        if restaurant:
            queryset = queryset.filter(restaurant_id=restaurant)

        # Поиск
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(position__icontains=search) |
                Q(user__email__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurants'] = Restaurant.objects.all()
        context['current_restaurant'] = self.request.GET.get('restaurant', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class StaffDetailView(LoginRequiredMixin, DetailView):
    """
    Подробная информация о сотруднике
    """
    model = Employee
    template_name = 'staff/detail.html'
    context_object_name = 'employee'

    def get_object(self):
        return get_object_or_404(
            Employee.objects.select_related('user', 'restaurant'),
            pk=self.kwargs['pk']
        )


class StaffCreateView(LoginRequiredMixin, CreateView):
    """
    Создание профиля сотрудника для существующего пользователя
    """
    model = Employee
    template_name = 'staff/form.html'
    fields = ['user', 'restaurant', 'position', 'photo']
    success_url = reverse_lazy('staff:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Добавить сотрудника'
        # Показываем только пользователей без профиля сотрудника
        context['available_users'] = CustomUser.objects.filter(employee__isnull=True)
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Сотрудник {form.instance.user.get_full_name()} успешно добавлен!')
        return super().form_valid(form)


class StaffUpdateView(LoginRequiredMixin, UpdateView):
    """
    Редактирование профиля сотрудника
    """
    model = Employee
    template_name = 'staff/form.html'
    fields = ['restaurant', 'position', 'photo']
    success_url = reverse_lazy('staff:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Редактировать: {self.object.user.get_full_name()}'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Информация о сотруднике обновлена!')
        return super().form_valid(form)