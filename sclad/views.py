import datetime

from django.http import HttpResponseForbidden
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from .models import Product, Arrival, Expense, Return, Writeoff, Supplier, Customer, ExpenseComposition
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView


def index(request):
    products = Product.objects.all()
    return render(request, 'sclad/index.html', {'products':products})

@login_required
def dashboard(request):
    user = request.user
    products = Product.objects.all()

    if user.role == 'admin':
        print("ADMIN!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # Админ видит все последние продажи, возвраты, списания и прибытия
        recent_expenses = Expense.objects.order_by('-date')[:5]
        recent_returns = Return.objects.order_by('-return_date')[:5]
        recent_writeoffs = Writeoff.objects.order_by('-writeoff_date')[:5]
        recent_arrivals = Arrival.objects.order_by('-date')[:5]
    elif user.role == 'manager':
        print("MANAGER!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # Менеджер видит только свои последние продажи за сегодня
        today = datetime.date.today()
        recent_expenses = Expense.objects.filter(user=user, date=today).order_by('-date')[:5]
        recent_returns = []
        recent_writeoffs = []
        recent_arrivals = Arrival.objects.order_by('-date')[:5]

    elif user.role == 'employee':
        print("EMPLOYEE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # Менеджер видит только свои последние продажи за сегодня
        recent_expenses = []
        recent_returns = []
        recent_writeoffs = []
        recent_arrivals = Arrival.objects.all()[:5]

    else:
        print("ТУТ НИКОГО НЕ ДОЛЖНО БЫТЬ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # Обычные пользователи не видят информацию о продажах, возвратах и списаниях
        recent_expenses = []
        recent_returns = []
        recent_writeoffs = []
        recent_arrivals = []

    context = {
        'products': products,
        'recent_expenses': recent_expenses,
        'recent_returns': recent_returns,
        'recent_writeoffs': recent_writeoffs,
        'recent_arrivals': recent_arrivals
    }

    return render(request, 'sclad/dashboard.html', context)

# @login_required
# def dashboard(request):
#     products = Product.objects.all()
#     arrivals = Arrival.objects.all().order_by('-id')
#     expenses = Expense.objects.all().order_by('-id')
#     returns = Return.objects.all().order_by('-id')
#     writeoffs = Writeoff.objects.all().order_by('-id')
#
#     context = {
#         'products': products,
#         'arrivals': arrivals[:5],
#         'expenses': expenses[:5],
#         'returns': returns[:5],
#         'writeoffs': writeoffs[:5],
#     }
#
#     if request.user.role == 'admin':
#         return render(request, 'sclad/dashboard.html', context)
#     elif request.user.role == 'manager':
#         manager_expenses = Expense.objects.filter(user=request.user).order_by('-id')[:5]
#         context['expenses'] = manager_expenses
#         return render(request, 'sclad/dashboard.html', context)
#     else:
#         return render(request, 'sclad/dashboard.html', context)



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
def expense_create(request):
    if request.user.role != 'manager':
        return HttpResponseForbidden("Только менеджеры могут создавать продажи.")

    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        customer = get_object_or_404(Customer, id=customer_id)
        date = request.POST.get('date')
        description = request.POST.get('description')
        expense = Expense.objects.create(
            customer=customer,
            date=date,
            description=description,
            user=request.user
        )

        for product_id, quantity in request.POST.items():
            if product_id.startswith('product_'):
                product_id = product_id.split('_')[1]
                product = get_object_or_404(Product, id=product_id)
                ExpenseComposition.objects.create(
                    expense=expense,
                    product=product,
                    quantity=int(quantity),
                    user=request.user
                )

        return redirect('sclad:expense_detail', expense_id=expense.id)
    else:
        customers = Customer.objects.all()
        products = Product.objects.all()
        return render(request, 'sclad/expense_create.html', {'customers': customers, 'products': products})


@login_required
def expense_detail(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    if request.user.role != 'admin' and request.user.role != 'manager' and expense.user != request.user:
        return HttpResponseForbidden("Вы не можете просматривать данную продажу.")

    return render(request, 'sclad/expense_detail.html', {'expense': expense})

# @login_required
# def expense_detail(request, expense_id):
#     expense = get_object_or_404(Expense, id=expense_id)
#
#     if request.user.role == 'admin' or expense.user == request.user:
#         # Логика для отображения деталей прибытия
#         context = {
#             'expense': expense,
#             # Другие данные для контекста
#         }
#         return render(request, 'sclad/expense_detail.html', context)
#     else:
#         return HttpResponseForbidden("You are not authorized to view this expense.")



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
