from django.urls import path
from . import views


app_name = 'sclad'

urlpatterns = [
    path('', views.index, name='index'),
    path('sclad/', views.dashboard, name='dashboard'),
    path('arrivals/<int:arrival_id>/', views.arrival_detail, name='arrival_detail'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:expense_id>/', views.expense_detail, name='expense_detail'),
]
