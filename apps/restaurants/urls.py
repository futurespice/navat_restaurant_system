# apps/restaurants/urls.py
from django.urls import path
from . import views

# app_name нужен для создания пространства имен.
# Это позволит нам использовать в шаблонах имена вида 'restaurants:detail'
# и избежать конфликтов, если в другом приложении тоже будет url с именем 'detail'.
app_name = 'restaurants'

urlpatterns = [
    # Список ресторанов будет на главной странице приложения
    path('', views.RestaurantListView.as_view(), name='list'),

    # Страница конкретного ресторана. <int:pk> - это id ресторана
    path('restaurant/<int:pk>/', views.RestaurantDetailView.as_view(), name='detail'),

    # Страница для создания нового ресторана
    path('restaurant/create/', views.RestaurantCreateView.as_view(), name='create'),
]