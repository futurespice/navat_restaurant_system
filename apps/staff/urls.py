# apps/staff/urls.py
from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.StaffListView.as_view(), name='list'),
    path('<int:pk>/', views.StaffDetailView.as_view(), name='detail'),
    path('create/', views.StaffCreateView.as_view(), name='create'),
    path('<int:pk>/update/', views.StaffUpdateView.as_view(), name='update'),
]