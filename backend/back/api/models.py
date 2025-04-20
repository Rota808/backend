from django.db import models

class Pizza(models.Model):
    pizza_name = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.URLField(max_length=500, blank=True, null=True)

class Size(models.Model):
    size_name = models.CharField(max_length=50)
    diameter = models.IntegerField()
    description = models.TextField()

class Beverage(models.Model):
    beverage_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image_url = models.URLField(max_length=500, blank=True, null=True)

class PizzaPrice(models.Model):
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)

class User(models.Model):
    full_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    saved_address = models.TextField()
    saved_info = models.BooleanField(default=False)

class StoreInfo(models.Model):
    address = models.TextField()
    directions = models.TextField()
    contact_phone = models.CharField(max_length=20)

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('payment_pending', 'Payment Pending'),
        ('completed', 'Completed'), 
        ('canceled', 'Canceled')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_address = models.TextField()
    contact_phone = models.CharField(max_length=20)
    estimated_delivery_time = models.CharField(max_length=50)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

class OrderItem(models.Model):
    ITEM_TYPES = [('pizza', 'Pizza'), ('beverage', 'Beverage')]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    pizza = models.ForeignKey(Pizza, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
    beverage = models.ForeignKey(Beverage, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)

# models.py
class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('cash', 'Cash'),
        ('pix', 'PIX'),
        ('mercadopago', 'Mercado Pago')
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    card_last_four = models.CharField(max_length=4, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    pix_qr_code = models.TextField(blank=True)
    mercado_pago_id = models.CharField(max_length=100, blank=True)
    mercado_pago_status = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)