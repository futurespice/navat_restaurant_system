# apps/analytics/urls.py
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Главный дашборд
    path('', views.DashboardView.as_view(), name='dashboard'),

    # API для получения данных графиков
    path('api/', views.AnalyticsAPIView.as_view(), name='analytics_api'),

    # Детальные отчеты (для будущего развития)
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('reports/sales/', views.SalesReportView.as_view(), name='sales_report'),
    path('reports/menu/', views.MenuReportView.as_view(), name='menu_report'),
    path('reports/branches/', views.BranchesReportView.as_view(), name='branches_report'),
]