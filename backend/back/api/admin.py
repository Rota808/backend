from django.contrib import admin
from .models import Pizza, Size, Beverage, PizzaPrice, User, StoreInfo, Order, OrderItem, Payment

# Register your models here.
admin.site.register(Pizza)
admin.site.register(Size)
admin.site.register(Beverage)
admin.site.register(PizzaPrice)
admin.site.register(User)
admin.site.register(StoreInfo)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)