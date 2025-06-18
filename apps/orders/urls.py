from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='detail'),
    path('<int:pk>/receipt/', views.OrderReceiptView.as_view(), name='receipt'),
    path('create/', views.OrderCreateView.as_view(), name='create'),
    path('<int:pk>/update/', views.OrderUpdateView.as_view(), name='update'),
    path('<int:pk>/process-ingredients/', views.ProcessIngredientsView.as_view(), name='process_ingredients'),
]