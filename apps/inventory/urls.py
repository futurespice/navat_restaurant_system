# apps/inventory/urls.py
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.InventoryDashboardView.as_view(), name='dashboard'),
    path('ingredients/', views.IngredientListView.as_view(), name='ingredients'),
    path('ingredients/create/', views.IngredientCreateView.as_view(), name='ingredient_create'),
    path('stock/', views.StockListView.as_view(), name='stock'),
    path('stock/<int:pk>/update/', views.StockUpdateView.as_view(), name='stock_update'),
    path('stock/add/', views.AddStockItemView.as_view(), name='add_stock_item'),
]