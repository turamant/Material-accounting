from math import ceil

from django.db import models

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

# class Warehouse(models.Model):
#     name = models.CharField(max_length=255)
#     user = models.ForeignKey('account.User', null=True, on_delete=models.CASCADE)
#
#
# class WarehouseRole(models.Model):
#     ROLE_CHOICES = [
#         ('admin', 'Admin'),
#         ('user', 'User'),
#     ]
#
#     warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
#     user = models.ForeignKey('account.User',null=True, on_delete=models.CASCADE)
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES)

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.TextField()
    user = models.ForeignKey('accounts.User', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Product(models.Model):
    article_number = models.CharField(max_length=50, unique=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    sell_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    user = models.ForeignKey('accounts.User', null=True, on_delete=models.CASCADE)

    @property
    def total_arrival_quantity(self):
        return sum(ac.quantity for ac in self.arrivalcomposition_set.all())

    @property
    def total_expense_quantity(self):
        return sum(ec.quantity for ec in self.expensecomposition_set.all())

    @property
    def balance_quantity(self):
        return self.total_arrival_quantity - self.total_expense_quantity

    @property
    def balance_value(self):
        return self.balance_quantity * self.purchase_price

    @property
    def balance_sell(self):
        return self.balance_quantity * self.sell_price

    @property
    def total_profit(self):
        total_revenue = 0
        for expense_composition in self.expensecomposition_set.all():
            expense = expense_composition.expense
            # Рассчитываем цену с учетом скидки клиента
            discounted_price = expense_composition.product.sell_price * (
                        1 - expense.customer.discount.discount_percentage / 100)
            total_revenue += discounted_price * expense_composition.quantity

        total_cost = sum(item.purchase_price * item.quantity for item in
                         self.arrivalcomposition_set.all()) + self.balance_quantity * self.purchase_price
        return total_revenue - total_cost

    def __str__(self):
        return f"{self.article_number} - {self.name}"


class Discount(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    discount_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey('accounts.User', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}: {self.discount_percentage}%'


class Customer(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.TextField()
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey('accounts.User', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Arrival(models.Model):
    date = models.DateField()
    description = models.TextField()
    supplier = models.ForeignKey(Supplier, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"Arrival on {self.date} from {self.supplier}, {self.description}"

    @property
    def total_arrival_cost(self):
        return sum(item.item_total for item in self.arrivalcomposition_set.all())

    @property
    def total_quant(self):
        return sum(item.quantity for item in self.arrivalcomposition_set.all())


class ArrivalComposition(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    arrival = models.ForeignKey(Arrival, on_delete=models.CASCADE)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    user = models.ForeignKey('accounts.User', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} in {self.arrival}"

    @property
    def item_total(self):
        return self.purchase_price * self.quantity


class Expense(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.TextField()
    user = models.ForeignKey('accounts.User', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"Дата: {self.date}, Покупатель: {self.customer}"

    @property
    def total_cost(self):
        total_cost = sum(item.product.sell_price * item.quantity for item in self.expensecomposition_set.all())
        if self.customer.discount:
            discount_percentage = self.customer.discount.discount_percentage / 100
            total_cost -= total_cost * discount_percentage
        return ceil(total_cost)

    @property
    def total_discount(self):
        total_cost = sum(item.product.sell_price * item.quantity for item in self.expensecomposition_set.all())
        if self.customer.discount:
            discount_percentage = self.customer.discount.discount_percentage / 100
        return ceil(total_cost * discount_percentage)


class ExpenseComposition(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    user = models.ForeignKey('accounts.User', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} in {self.expense}"

    @property
    def discount_amount(self):
        if self.expense.customer.discount:
            discounted_price = self.product.sell_price * (1 - self.expense.customer.discount.discount_percentage / 100)
            return (self.product.sell_price - discounted_price) * self.quantity
        return 0

    @property
    def total_price(self):
        if self.expense.customer.discount:
            discounted_price = self.product.sell_price * (1 - self.expense.customer.discount.discount_percentage / 100)
            return discounted_price * self.quantity
        return self.product.sell_price * self.quantity


class Return(models.Model):
    expense_composition = models.ForeignKey(ExpenseComposition, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    reason = models.TextField()
    return_date = models.DateField()
    sell_price = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey('accounts.User', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"Return of {self.quantity} {self.expense_composition.product.name}"


class Writeoff(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    reason = models.TextField()
    writeoff_date = models.DateField()
    user = models.ForeignKey('accounts.User', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"Writeoff of {self.quantity} {self.product.name} from {self.supplier.name}"



# signals ----------

@receiver(post_save, sender=Expense)
def create_expense_compositions(sender, instance, created, **kwargs):
    if created:
        for expense_composition in instance.expensecomposition_set.all():
            expense_composition.expense = instance
            expense_composition.save()


@receiver(post_save, sender=ExpenseComposition)
def update_product_quantity(sender, instance, **kwargs):
    product = instance.product
    product.quantity -= instance.quantity
    product.save()


@receiver(post_save, sender=ArrivalComposition)
def update_product_purchase_price(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        total_purchase_cost = product.purchase_price * product.quantity
        total_purchase_cost += instance.quantity * instance.purchase_price
        product.quantity += instance.quantity
        product.purchase_price = total_purchase_cost / product.quantity
        product.save()


@receiver(post_delete, sender=Expense)
def update_product_quantity(sender, instance, **kwargs):
    try:
        for expense_composition in instance.expensecomposition_set.all():
            product = expense_composition.product
            product.quantity += expense_composition.quantity
            product.save()
    except (ExpenseComposition.DoesNotExist, Product.DoesNotExist):
        pass
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")


@receiver(post_save, sender=Return)
def update_product_quantity_on_return(sender, instance, created, **kwargs):
    if created:
        product = instance.expense_composition.product
        product.quantity += instance.quantity
        product.save()


@receiver(post_delete, sender=Return)
def update_product_quantity_on_return_delete(sender, instance, **kwargs):
    product = instance.expense_composition.product
    product.quantity -= instance.quantity
    product.save()


@receiver(post_save, sender=Writeoff)
def update_product_quantity_on_writeoff(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.quantity -= instance.quantity
        product.save()


@receiver(post_delete, sender=Writeoff)
def update_product_quantity_on_writeoff_delete(sender, instance, **kwargs):
    product = instance.product
    product.quantity += instance.quantity
    product.save()



