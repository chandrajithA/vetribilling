from django.db import models



class Invoice(models.Model):
    customer_name = models.CharField(max_length=200)
    customer_mobile = models.CharField(max_length=15)
    customer_email = models.EmailField()
    customer_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    

    @property
    def sub_total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def tax_amount(self):
        return sum(item.tax_amount for item in self.items.all())

    @property
    def total_with_tax(self):
        return sum(item.total_with_tax for item in self.items.all())
    
    @property
    def total_amount(self):
        return self.total_with_tax   # alias
    

    def __str__(self):
        return f"Invoice {self.id} - {self.customer_name}"



class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    @property
    def tax_amount(self):
        return (self.unit_price * self.quantity) * (self.tax_percentage / 100)

    @property
    def total_with_tax(self):
        return self.subtotal + self.tax_amount

    def __str__(self):
        return f"{self.product_name} ({self.invoice.id})"
