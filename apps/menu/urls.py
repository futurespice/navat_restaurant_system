# apps/menu/urls.py
from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    # Список всех блюд
    path('', views.MenuListView.as_view(), name='list'),

    # Создание нового блюда
    path('item/create/', views.MenuItemCreateView.as_view(), name='item_create'),

    # Редактирование существующего блюда
    path('item/<int:pk>/update/', views.MenuItemUpdateView.as_view(), name='item_update'),

    # Удаление блюда
    path('item/<int:pk>/delete/', views.MenuItemDeleteView.as_view(), name='item_delete'),

    # Мы также можем добавить CRUD для категорий, если понадобится.
    # Например, path('categories/', views.CategoryListView.as_view(), name='category_list'),
]