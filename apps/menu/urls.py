# apps/menu/urls.py
from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    # Основные страницы меню
    path('', views.MenuListView.as_view(), name='list'),

    # CRUD для блюд
    path('item/create/', views.MenuItemCreateView.as_view(), name='item_create'),
    path('item/<int:pk>/update/', views.MenuItemUpdateView.as_view(), name='item_update'),
    path('item/<int:pk>/delete/', views.MenuItemDeleteView.as_view(), name='item_delete'),

    # CRUD для категорий
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # AJAX endpoints
    path('ajax/dish/<int:pk>/toggle-availability/', views.toggle_dish_availability, name='toggle_dish_availability'),
    path('ajax/category/<int:category_id>/dishes/', views.get_category_dishes, name='get_category_dishes'),
]