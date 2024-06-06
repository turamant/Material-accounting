import datetime
from decimal import Decimal
from django.forms import inlineformset_factory

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.shortcuts import render

from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import ProductForm, ArrivalForm, ExpenseForm, CustomerForm, ExpenseCompositionForm
from .models import Product, Arrival, Expense, Return, Writeoff, Supplier, Customer, ExpenseComposition, \
    ArrivalComposition, Discount
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView

@login_required
def supplier_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        contact_info = request.POST.get('contact_info')
        Supplier.objects.create(
            name=name,
            contact_info=contact_info,
            user=request.user
        )
        return redirect('sclad:supplier_list')
    return render(request, 'sclad/supplier_create.html')

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.filter(user=request.user)
    return render(request, 'sclad/supplier_list.html', {'suppliers': suppliers})


@login_required
def discount_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        discount_percentage = request.POST.get('discount_percentage')
        Discount.objects.create(
            name=name,
            description=description,
            discount_percentage=discount_percentage,
            user=request.user
        )
        return redirect('sclad:discount_list')
    return render(request, 'sclad/discount_create.html')

@login_required
def discount_list(request):
    discounts = Discount.objects.filter(user=request.user)
    return render(request, 'sclad/discount_list.html', {'discounts': discounts})


@login_required
def customer_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        contact_info = request.POST.get('contact_info')
        discount_id = request.POST.get('discount')
        discount = None
        if discount_id:
            discount = Discount.objects.get(id=discount_id, user=request.user)
        customer = Customer.objects.create(
            name=name,
            contact_info=contact_info,
            discount=discount,
            user=request.user
        )
        return redirect('sclad:customer_list')
    discounts = Discount.objects.filter(user=request.user)
    return render(request, 'sclad/customer_create.html', {'discounts': discounts})

@login_required
def customer_list(request):
    customers = Customer.objects.filter(user=request.user)
    return render(request, 'sclad/customer_list.html', {'customers': customers})


def index(request):
    products = Product.objects.all()
    return render(request, 'sclad/index.html', {'products':products})

@login_required
def dashboard(request):
    products = Product.objects.filter(user=request.user).order_by('-id')
    recent_expenses = Expense.objects.filter(user=request.user).order_by('-date', '-id')[:5]
    recent_returns = Return.objects.filter(user=request.user).order_by('-return_date')[:5]
    recent_writeoffs = Writeoff.objects.filter(user=request.user).order_by('-writeoff_date')[:5]
    recent_arrivals = Arrival.objects.filter(user=request.user).order_by('-date','-id')[:5]

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
#     user = request.user
#     products = Product.objects.all().order_by('-id')
#
#     if user.role == 'admin':
#         print("ADMIN!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
#         # Админ видит все последние продажи, возвраты, списания и прибытия
#         recent_expenses = Expense.objects.order_by('-date', '-id')[:5]
#         recent_returns = Return.objects.order_by('-return_date')[:5]
#         recent_writeoffs = Writeoff.objects.order_by('-writeoff_date')[:5]
#         recent_arrivals = Arrival.objects.order_by('-date','-id')[:5]
#     elif user.role == 'manager':
#         print("MANAGER!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
#         # Менеджер видит только свои последние продажи за сегодня
#         today = datetime.date.today()
#         recent_expenses = Expense.objects.filter(store=user.store, date=today).order_by('-date','-id')[:5]
#         recent_returns = []
#         recent_writeoffs = []
#         recent_arrivals = Arrival.objects.order_by('-date','-id')[:5]
#
#     elif user.role == 'employee':
#         print("EMPLOYEE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
#         # Менеджер видит только свои последние продажи за сегодня
#         recent_expenses = []
#         recent_returns = []
#         recent_writeoffs = []
#         recent_arrivals = Arrival.objects.filter(store=user.store)[:5]
#
#     else:
#         print("ТУТ НИКОГО НЕ ДОЛЖНО БЫТЬ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
#         # Обычные пользователи не видят информацию о продажах, возвратах и списаниях
#         recent_expenses = []
#         recent_returns = []
#         recent_writeoffs = []
#         recent_arrivals = []
#
#     context = {
#         'products': products,
#         'recent_expenses': recent_expenses,
#         'recent_returns': recent_returns,
#         'recent_writeoffs': recent_writeoffs,
#         'recent_arrivals': recent_arrivals
#     }
#
#     return render(request, 'sclad/dashboard.html', context)

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
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            return redirect('sclad:dashboard')
    else:
        form = ProductForm()

    return render(request, 'sclad/product_form.html', {'form': form})


# class ProductDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
#     model = Product
#     template_name = 'sclad/product_detail.html'
#
#     def get_object(self, queryset=None):
#         return get_object_or_404(Product, pk=self.kwargs['pk'])
#
#     def test_func(self):
#         product = self.get_object()
#         return self.request.user.role == 'admin' or product.user == self.request.user


@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product,
    }
    return render(request, 'sclad/product_detail.html', context)

# @login_required
# def arrival_create(request):
#     if request.user.role != 'admin':
#         return HttpResponseForbidden("Только администраторы могут создавать приходы.")
#
#     ArrivalCompositionFormSet = inlineformset_factory(
#         Arrival, ArrivalComposition, fields=('product', 'quantity', 'purchase_price'), extra=1, can_delete=False
#     )
#
#     if request.method == 'POST':
#         arrival_form = ArrivalForm(request.POST)
#         arrival_composition_formset = ArrivalCompositionFormSet(request.POST, prefix='composition')
#
#         if arrival_form.is_valid() and arrival_composition_formset.is_valid():
#             arrival = arrival_form.save(commit=False)
#             arrival.user = request.user
#             arrival.save()
#
#             for form in arrival_composition_formset:
#                 arrival_composition = form.save(commit=False)
#                 arrival_composition.arrival = arrival
#                 arrival_composition.user = request.user
#                 arrival_composition.save()
#
#             return redirect('sclad:arrival_detail', arrival_id=arrival.id)
#     else:
#         arrival_form = ArrivalForm()
#         arrival_composition_formset = ArrivalCompositionFormSet(prefix='composition')
#
#     return render(request, 'sclad/arrival_create.html', {
#         'arrival_form': arrival_form,
#         'arrival_composition_formset': arrival_composition_formset
#     })

@login_required
def arrival_create(request):
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        supplier = get_object_or_404(Supplier, id=supplier_id, user=request.user)
        date = request.POST.get('date')
        description = request.POST.get('description')
        arrival = Arrival.objects.create(
            supplier=supplier,
            date=date,
            description=description,
            user=request.user
        )

        for key, value in request.POST.items():
            if key.startswith('product_'):
                product_id = key.split('_')[1]
                product = get_object_or_404(Product, id=product_id, user=request.user)
                if value:
                    quantity = int(value)
                    ArrivalComposition.objects.create(
                        arrival=arrival,
                        product=product,
                        purchase_price=product.purchase_price,
                        quantity=quantity,
                        user=request.user
                    )

        return redirect('sclad:arrival_detail', arrival_id=arrival.id)
    else:
        suppliers = Supplier.objects.filter(user=request.user)
        products = Product.objects.filter(user=request.user)
        return render(request, 'sclad/arrival_create.html', {'suppliers': suppliers, 'products': products})


@login_required
def arrival_detail(request, arrival_id):
    arrival = get_object_or_404(Arrival, id=arrival_id)
    context = {
        'arrival': arrival,

            # Другие данные для контекста
        }
    return render(request, 'sclad/arrival_detail.html', context)


@login_required
def expense_create(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        customer = get_object_or_404(Customer, id=customer_id, user=request.user)
        date = request.POST.get('date')
        description = request.POST.get('description')
        expense = Expense.objects.create(
            customer=customer,
            date=date,
            description=description,
            user=request.user
        )

        for key, value in request.POST.items():
            if key.startswith('product_'):
                product_id = key.split('_')[1]
                product = get_object_or_404(Product, id=product_id)
                if value:  # проверьте, не пустая ли строка
                    quantity = int(value)  # преобразуйте value в целое число
                    if quantity > 0:
                        ExpenseComposition.objects.create(
                            expense=expense,
                            product=product,
                            quantity=quantity,
                            user=request.user
                        )

        return redirect('sclad:expense_detail', expense_id=expense.id)
    else:
        customers = Customer.objects.filter(user=request.user)
        products = Product.objects.filter(user=request.user)
        return render(request, 'sclad/expense_create.html', {'customers': customers, 'products': products})

# def expense_create(request):
#     ExpenseCompositionFormSet = inlineformset_factory(
#         Expense, ExpenseComposition, fields=('product', 'quantity'), extra=1, can_delete=False
#     )
#
#     if request.method == 'POST':
#         expense_form = ExpenseForm(request.POST)
#         expense_composition_formset = ExpenseCompositionFormSet(request.POST, prefix='composition')
#
#         if expense_form.is_valid() and expense_composition_formset.is_valid():
#             expense = expense_form.save(commit=False)
#             expense.user = request.user
#             expense.save()
#
#             for form in expense_composition_formset:
#                 expense_composition = form.save(commit=False)
#                 expense_composition.expense = expense
#                 expense_composition.user = request.user
#                 expense_composition.save()
#
#             return redirect('sclad:expense_detail', expense_id=expense.id)
#     else:
#         expense_form = ExpenseForm()
#         expense_composition_formset = ExpenseCompositionFormSet(prefix='composition')
#
#     return render(request, 'sclad/expense_create.html', {
#         'expense_form': expense_form,
#         'expense_composition_formset': expense_composition_formset
#     })

@login_required
def expense_detail(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
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
