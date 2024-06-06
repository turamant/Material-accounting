from django.contrib import admin
from .models import (Supplier, Product, Discount, Customer, Arrival,
                     ArrivalComposition, Expense, ExpenseComposition, Return, Writeoff)



class ArrivalCompositionInline(admin.TabularInline):
    model = ArrivalComposition
    extra = 1


class ArrivalAdmin(admin.ModelAdmin):
    inlines = [ArrivalCompositionInline]

    def __str__(self):
        if self.supplier:
            return f"Arrival on {self.date} from {self.supplier.name}"
        else:
            return f"Arrival on {self.date}"


class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_info']


class ExpenseCompositionInline(admin.TabularInline):
    model = ExpenseComposition
    extra = 1


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('customer', 'date', 'description', 'discount_percentage', 'total_cost')

    inlines = [ExpenseCompositionInline]

    def __str__(self):
        return f"Expense for {self.customer.name} on {self.date}, :{self.total_cost}"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    @admin.display(description='Discount')
    def discount_percentage(self, obj):
        if obj.customer.discount:
            return f"{obj.customer.discount.discount_percentage}%"
        return "-"


class ArrivalCompositionAdmin(admin.ModelAdmin):
    list_display = ('product', 'arrival', 'quantity', 'purchase_price')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('article_number', 'name', 'quantity', 'total_arrival_quantity',
                    'total_expense_quantity', 'balance_quantity',
                    'balance_value', 'balance_sell', 'total_profit')


admin.site.register(Writeoff)
admin.site.register(Return)
admin.site.register(Product, ProductAdmin)

admin.site.register(ArrivalComposition, ArrivalCompositionAdmin)
admin.site.register(Supplier)
admin.site.register(Discount)
admin.site.register(Customer)
admin.site.register(Arrival, ArrivalAdmin)

admin.site.register(Expense, ExpenseAdmin)
admin.site.register(ExpenseComposition)



