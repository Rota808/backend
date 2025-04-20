from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import mercadopago
import os
from datetime import datetime, timedelta
import logging
from .serializers import *

logger = logging.getLogger(__name__)

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

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    @action(detail=True, methods=['post'])
    def create_mercado_pago_preference(self, request, pk=None):
        """Create Mercado Pago checkout preference for an order"""
        order = self.get_object()
        
        # Initialize MercadoPago SDK
        access_token = os.getenv('MERCADOPAGO_ACCESS_TOKEN')
        if not access_token:
            logger.error("MercadoPago access token not configured")
            return Response(
                {'error': 'Payment gateway not configured'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        sdk = mercadopago.SDK(access_token)
        
        # Prepare items - use either from request or from order
        items = request.data.get('items', [])
        if not items:
            items = []
            for item in order.items.all():
                if item.item_type == 'pizza':
                    title = f"{item.pizza.pizza_name} ({item.size.size_name})"
                    unit_price = float(item.price)
                else:
                    title = item.beverage.beverage_name
                    unit_price = float(item.beverage.price)
                    
                items.append({
                    "id": str(item.id),
                    "title": title,
                    "description": title,
                    "category_id": "food",
                    "quantity": item.quantity,
                    "unit_price": unit_price,
                    "currency_id": "BRL"
                })
        
        # Get payer info from request or order
        payer_email = request.data.get('payer', {}).get('email', '')
        if not payer_email and order.user.email:
            payer_email = order.user.email
            
        # Create preference data
        preference_data = {
            "items": items,
            "payer": {
                "email": payer_email,
                "name": order.user.full_name,
                "phone": {
                    "area_code": "",  # Brazil specific, can extract from phone
                    "number": request.data.get('payer', {}).get('phone') or order.contact_phone
                },
            },
            "payment_methods": {
                "excluded_payment_types": [{"id": "atm"}],
                "installments": 1,
                "default_installments": 1
            },
            "binary_mode": True,
            "auto_return": "approved",
            "back_urls": {
                "success": request.build_absolute_uri(f'/order/{order.id}/success'),
                "failure": request.build_absolute_uri(f'/order/{order.id}/failure'),
                "pending": request.build_absolute_uri(f'/order/{order.id}/pending')
            },
            "notification_url": request.build_absolute_uri('/api/payments/webhook/'),
            "external_reference": str(order.id),
            "statement_descriptor": "PIZZARIA",
            "date_of_expiration": (datetime.now() + timedelta(hours=24)).isoformat() + ".000-04:00"
        }
        
        try:
            # Create preference
            preference_response = sdk.preference().create(preference_data)
            
            if preference_response['status'] not in [200, 201]:
                logger.error(f"MercadoPago API error: {preference_response}")
                return Response(
                    preference_response['response'],
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            preference = preference_response["response"]
            
            # Create payment record
            payment, created = Payment.objects.update_or_create(
                order=order,
                defaults={
                    'payment_method': 'mercado_pago',
                    'payment_status': 'pending',
                    'transaction_id': preference['id'],
                    'mercado_pago_id': preference['id'],
                    'mercado_pago_status': 'pending'
                }
            )
            
            return Response({
                'preference_id': preference['id'],
                'init_point': preference['init_point'],
                'sandbox_init_point': preference.get('sandbox_init_point'),
                'payment_id': payment.id
            })
            
        except Exception as e:
            logger.error(f"Error creating MercadoPago preference: {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def test_mercado_pago(self, request):
        """Test endpoint for Mercado Pago integration"""
        access_token = os.getenv('MERCADOPAGO_ACCESS_TOKEN')
        if not access_token:
            return Response(
                {'error': 'MercadoPago access token not configured'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        sdk = mercadopago.SDK(access_token)
        
        test_data = {
            "items": [
                {
                    "title": "Test Item",
                    "quantity": 1,
                    "unit_price": 10.50,
                    "currency_id": "BRL"
                }
            ],
            "payer": {
                "email": "test@example.com"
            },
            "binary_mode": True
        }
        
        try:
            response = sdk.preference().create(test_data)
            return Response(response)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )