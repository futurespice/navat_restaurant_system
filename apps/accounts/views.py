from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import CustomUser
from .forms import CustomLoginForm, UserRegistrationForm, UserProfileForm


class CustomLoginView(LoginView):
    """Кастомная страница входа"""
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return reverse_lazy('analytics:dashboard')
        elif user.role == 'MANAGER':
            return reverse_lazy('analytics:dashboard')
        else:
            return reverse_lazy('orders:pos')


class CustomLogoutView(LogoutView):
    """Выход из системы"""
    next_page = 'accounts:login'


class ProfileView(LoginRequiredMixin, TemplateView):
    """Профиль пользователя"""
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        # Проверяем, есть ли профиль сотрудника
        if hasattr(self.request.user, 'employee'):
            context['employee'] = self.request.user.employee
        return context


class UserManagementView(LoginRequiredMixin, ListView):
    """Управление пользователями (только для админов)"""
    model = CustomUser
    template_name = 'accounts/user_management.html'
    context_object_name = 'users'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'ADMIN':
            messages.error(request, 'У вас нет прав для доступа к этой странице')
            return redirect('analytics:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return CustomUser.objects.all().order_by('-date_joined')


class CreateUserView(LoginRequiredMixin, CreateView):
    """Создание нового пользователя"""
    model = CustomUser
    form_class = UserRegistrationForm
    template_name = 'accounts/create_user.html'
    success_url = reverse_lazy('accounts:user_management')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'ADMIN':
            messages.error(request, 'У вас нет прав для создания пользователей')
            return redirect('analytics:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, f'Пользователь {form.instance.get_full_name()} создан!')
        return super().form_valid(form)


class EditUserView(LoginRequiredMixin, UpdateView):
    """Редактирование пользователя"""
    model = CustomUser
    form_class = UserProfileForm
    template_name = 'accounts/edit_user.html'
    success_url = reverse_lazy('accounts:user_management')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'ADMIN':
            messages.error(request, 'У вас нет прав для редактирования пользователей')
            return redirect('analytics:dashboard')
        return super().dispatch(request, *args, **kwargs)


@login_required
def create_staff_from_user(request, user_id):
    """Быстрое создание профиля сотрудника для существующего пользователя"""
    if request.user.role not in ['ADMIN', 'MANAGER']:
        messages.error(request, 'У вас нет прав для этого действия')
        return redirect('accounts:user_management')

    user = get_object_or_404(CustomUser, id=user_id)

    if hasattr(user, 'employee'):
        messages.warning(request, 'У этого пользователя уже есть профиль сотрудника')
        return redirect('accounts:user_management')

    if request.method == 'POST':
        from apps.staff.models import Employee
        from apps.restaurants.models import Restaurant

        restaurant_id = request.POST.get('restaurant')
        position = request.POST.get('position')

        if restaurant_id and position:
            restaurant = Restaurant.objects.get(id=restaurant_id)
            Employee.objects.create(
                user=user,
                restaurant=restaurant,
                position=position
            )
            messages.success(request, f'Профиль сотрудника для {user.get_full_name()} создан!')
            return redirect('staff:list')
        else:
            messages.error(request, 'Заполните все обязательные поля')

    from apps.restaurants.models import Restaurant
    return render(request, 'accounts/create_staff_profile.html', {
        'user': user,
        'restaurants': Restaurant.objects.all()
    })