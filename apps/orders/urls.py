# apps/orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='detail'),
    path('create/', views.OrderCreateView.as_view(), name='create'),
    path('<int:order_id>/add-item/', views.AddItemToOrderView.as_view(), name='add_item'),
    path('<int:pk>/update-status/', views.UpdateOrderStatusView.as_view(), name='update_status'),
]