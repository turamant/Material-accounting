from django.urls import path
from . import views


app_name = 'sclad'

urlpatterns = [
    path('', views.index, name='index'),
    path('sclad/', views.dashboard, name='dashboard'),
    path('arrivals/<int:arrival_id>/', views.arrival_detail, name='arrival_detail'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:expense_id>/', views.expense_detail, name='expense_detail'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('arrivals/create/', views.arrival_create, name='arrival_create'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('discounts/create/', views.discount_create, name='discount_create'),
    path('discounts/', views.discount_list, name='discount_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/', views.customer_list, name='customer_list'),
]
