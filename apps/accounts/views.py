# apps/accounts/views.py
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy


class CustomLoginView(LoginView):
    """
    Красивая страница входа в систему
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('analytics:dashboard')


class CustomLogoutView(LogoutView):
    """
    Выход из системы с перенаправлением
    """
    next_page = 'accounts:login'


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Профиль пользователя
    """
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем информацию о сотруднике, если есть
        try:
            context['employee'] = self.request.user.employee
        except:
            context['employee'] = None
        return context