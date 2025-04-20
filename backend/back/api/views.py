from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
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
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def create_mercado_pago_preference(self, request, pk=None):
        """Cria uma preferência de pagamento no Mercado Pago para um pedido"""
        try:
            order = self.get_object()

            # Inicializa SDK do Mercado Pago
            access_token = 'APP_USR-4911686956582688-041816-31668dad46e92a52be9f0816640dada6-2225972856'
            if not access_token:
                logger.error("Access token do MercadoPago não configurado.")
                return Response({'error': 'Configuração de pagamento ausente.'}, status=500)

            sdk = mercadopago.SDK(access_token)

            # Processa os itens
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

            payer_email = request.data.get('payer', {}).get('email', '')
            payer_phone = request.data.get('payer', {}).get('phone') or order.contact_phone

            # Data de expiração formatada corretamente com fuso horário -03:00
            from datetime import timezone
            br_tz = timezone(timedelta(hours=-3))
            expiration_date = (datetime.now(br_tz) + timedelta(hours=24)).isoformat()

            preference_data = {
                "items": items,
                "payer": {
                    "email": payer_email,
                    "name": order.user.full_name,
                    "phone": {
                        "area_code": "",
                        "number": payer_phone
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
                "date_of_expiration": expiration_date
            }

            preference_response = sdk.preference().create(preference_data)

            if preference_response['status'] not in [200, 201]:
                logger.error(f"Erro na API do MercadoPago: {preference_response}")
                return Response(preference_response['response'], status=400)

            preference = preference_response['response']

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
            logger.exception("Erro ao criar preferência MercadoPago:")
            return Response({'error': str(e)}, status=400)

    
    @action(detail=False, methods=['post'])
    def test_mercado_pago(self, request):
        """Test endpoint for Mercado Pago integration"""
        access_token = 'APP_USR-4911686956582688-041816-31668dad46e92a52be9f0816640dada6-2225972856'
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
            
    @api_view(['POST'])
    @permission_classes([AllowAny])
    def mercadopago_webhook(request):
        """
        Webhook to receive payment notifications from MercadoPago
        """
        try:
            # Initialize MercadoPago SDK with your access token
            access_token = 'APP_USR-4911686956582688-041816-31668dad46e92a52be9f0816640dada6-2225972856'
            sdk = mercadopago.SDK(access_token)
            
            # Log the incoming webhook
            logger.info(f"MercadoPago webhook received: {request.data}")
            
            # Get the topic and ID from the notification
            topic = request.query_params.get('topic', '') or request.query_params.get('type', '')
            resource_id = request.query_params.get('id', '')
            
            if not topic or not resource_id:
                logger.error("Missing topic or ID in MercadoPago webhook")
                return Response({"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Process based on notification type
            if topic == 'payment':
                # Get payment information from MercadoPago API
                payment_info = sdk.payment().get(resource_id)
                
                if payment_info["status"] != 200:
                    logger.error(f"Failed to get payment info: {payment_info}")
                    return Response({"error": "Failed to get payment info"}, status=status.HTTP_400_BAD_REQUEST)
                
                payment_data = payment_info["response"]
                
                # Get MercadoPago status
                mp_status = payment_data["status"]
                
                # Get the order ID from external_reference
                order_id = payment_data.get("external_reference")
                if not order_id:
                    logger.error("Missing external_reference in payment data")
                    return Response({"error": "Missing order reference"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Find the payment record
                try:
                    payment = Payment.objects.get(order__id=order_id)
                except Payment.DoesNotExist:
                    logger.error(f"Payment not found for order: {order_id}")
                    return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
                
                # Update payment status based on MercadoPago status
                payment_status_mapping = {
                    'approved': 'paid',
                    'pending': 'pending',
                    'in_process': 'pending',
                    'rejected': 'failed',
                    'refunded': 'refunded',
                    'cancelled': 'failed',
                    'in_mediation': 'pending',
                    'charged_back': 'failed'
                }
                
                payment.payment_status = payment_status_mapping.get(mp_status, 'pending')
                payment.mercado_pago_status = mp_status
                payment.transaction_id = payment_data["id"]
                payment.save()
                
                # Update order status if payment is approved
                if mp_status == 'approved':
                    order = payment.order
                    order.status = 'completed'
                    order.save()
                
                logger.info(f"Payment status updated: {payment.id} -> {payment.payment_status}")
                return Response({"status": "success"}, status=status.HTTP_200_OK)
                
            elif topic == 'merchant_order':
                # Handle merchant_order notifications if needed
                return Response({"status": "success"}, status=status.HTTP_200_OK)
            
            else:
                logger.warning(f"Unhandled MercadoPago webhook topic: {topic}")
                return Response({"status": "ignored"}, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error processing MercadoPago webhook: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        """Manually confirm a payment (for client-side confirmation)"""
        payment = self.get_object()
        status_value = request.data.get('status')
        
        if not status_value:
            return Response(
                {'error': 'Status value is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Map status from request to internal payment status
        status_mapping = {
            'approved': 'paid',
            'pending': 'pending',
            'rejected': 'failed',
            'refunded': 'refunded'
        }
        
        payment_status = status_mapping.get(status_value, 'pending')
        
        # Update payment
        payment.payment_status = payment_status
        payment.mercado_pago_status = status_value
        payment.save()
        
        # Update order status if payment is approved
        if payment_status == 'paid':
            order = payment.order
            order.status = 'completed'
            order.save()
        
        return Response({
            'status': 'success',
            'payment_status': payment.payment_status,
            'order_status': payment.order.status
        })