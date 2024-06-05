from django.http import HttpResponseForbidden
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from .models import Product, Arrival, Expense, Return, Writeoff, Supplier
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView


def index(request):
    products = Product.objects.all()
    return render(request, 'sclad/index.html', {'products':products})

@login_required()
def dashboard(request):
    user = request.user
    if user.role == 'admin':
        products = Product.objects.all()
        recent_arrivals = Arrival.objects.order_by('-date')[:5]
        recent_expenses = Expense.objects.order_by('-date')[:5]
        recent_returns = Return.objects.order_by('-return_date')[:5]
        recent_writeoffs = Writeoff.objects.order_by('-writeoff_date')[:5]

    elif user.role == 'manager':
        products = Product.objects.all()
        recent_arrivals = []
        recent_expenses = Expense.objects.order_by('-date')[:5]
        recent_returns = Return.objects.order_by('-return_date')[:5]
        recent_writeoffs = Writeoff.objects.order_by('-writeoff_date')[:5]
    else:
        products = Product.objects.filter(user=user)
        recent_arrivals = Arrival.objects.filter(user=user)[:5]
        recent_expenses = Expense.objects.filter(user=user)[:5]
        recent_returns = Return.objects.filter(user=user)[:5]
        recent_writeoffs = Writeoff.objects.filter(user=user)[:5]

    context = {
        'products': products,
        'recent_arrivals': recent_arrivals,
        'recent_expenses': recent_expenses,
        'recent_returns': recent_returns,
        'recent_writeoffs': recent_writeoffs
    }

    return render(request, 'sclad/dashboard.html', context)


@login_required
def arrival_detail(request, arrival_id):
    arrival = get_object_or_404(Arrival, id=arrival_id)

    if request.user.role == 'admin' or arrival.user == request.user:
        # Логика для отображения деталей прибытия
        context = {
            'arrival': arrival,
            # Другие данные для контекста
        }
        return render(request, 'sclad/arrival_detail.html', context)
    else:
        return HttpResponseForbidden("You are not authorized to view this arrival.")


@login_required
def expense_detail(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)

    if request.user.role == 'admin' or expense.user == request.user:
        # Логика для отображения деталей прибытия
        context = {
            'expense': expense,
            # Другие данные для контекста
        }
        return render(request, 'sclad/expense_detail.html', context)
    else:
        return HttpResponseForbidden("You are not authorized to view this expense.")



class ProductListView(ListView):
    model = Product
    template_name = 'sclad/product_list.html'
    context_object_name = 'products'


class ProductDetailView(DetailView):
    model = Product
    template_name = 'sclad/arrival_detail.html'


class ProductCreateView(CreateView):
    model = Product
    fields = ['article_number', 'name', 'description', 'purchase_price', 'sell_price', 'quantity']
    template_name = 'inventory/product_form.html'


class ProductUpdateView(UpdateView):
    model = Product
    fields = ['article_number', 'name', 'description', 'purchase_price', 'sell_price', 'quantity']
    template_name = 'inventory/product_form.html'


class SupplierListView(ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'


class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'inventory/supplier_detail.html'


class SupplierCreateView(CreateView):
    model = Supplier
    fields = ['name', 'contact_info']
    template_name = 'inventory/supplier_form.html'


class SupplierUpdateView(UpdateView):
    model = Supplier
    fields = ['name', 'contact_info']
    template_name = 'inventory/supplier_form.html'
