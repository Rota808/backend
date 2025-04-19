from rest_framework import viewsets
from .models import *
from .serializers import *

class PizzaViewSet(viewsets.ModelViewSet):
    queryset = Pizza.objects.all()
    serializer_class = PizzaSerializer

class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer

class BeverageViewSet(viewsets.ModelViewSet):
    queryset = Beverage.objects.all()
    serializer_class = BeverageSerializer

class PizzaPriceViewSet(viewsets.ModelViewSet):
    queryset = PizzaPrice.objects.all()
    serializer_class = PizzaPriceSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class StoreInfoViewSet(viewsets.ModelViewSet):
    queryset = StoreInfo.objects.all()
    serializer_class = StoreInfoSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

# views.py
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import mercadopago
import os
from datetime import datetime

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    @action(detail=True, methods=['post'])
    def create_mercado_pago_preference(self, request, pk=None):
        order = self.get_object()
        
        # Initialize MercadoPago SDK
        sdk = mercadopago.SDK(os.getenv('MERCADOPAGO_ACCESS_TOKEN'))
        
        # Get order items
        order_items = []
        for item in order.items.all():
            if item.item_type == 'pizza':
                title = f"{item.pizza.pizza_name} ({item.size.size_name})"
                unit_price = float(item.price)
            else:
                title = item.beverage.beverage_name
                unit_price = float(item.beverage.price)
                
            order_items.append({
                "title": title,
                "unit_price": unit_price,
                "quantity": item.quantity,
            })
        
        # Create preference data
        preference_data = {
            "items": order_items,
            "payer": {
                "name": order.user.full_name,
                "phone": {
                    "number": order.contact_phone
                },
            },
            "external_reference": str(order.id),  # Link to your order ID
            "notification_url": request.build_absolute_uri('/api/payments/webhook/'),
            "back_urls": {
                "success": request.build_absolute_uri(f'/order/{order.id}/success'),
                "failure": request.build_absolute_uri(f'/order/{order.id}/failure'),
                "pending": request.build_absolute_uri(f'/order/{order.id}/pending')
            },
            "auto_return": "approved",
            "statement_descriptor": "PIZZARIA",  # Will appear on customer's statement
        }
        
        try:
            # Create preference
            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]
            
            # Create or update payment record
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'payment_method': 'mercado_pago',
                    'transaction_id': preference['id'],
                    'mercado_pago_id': preference['id'],
                }
            )
            
            if not created:
                payment.transaction_id = preference['id']
                payment.mercado_pago_id = preference['id']
                payment.save()
            
            return Response({
                'preference_id': preference['id'],
                'init_point': preference['init_point'],
                'sandbox_init_point': preference['sandbox_init_point'],
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )