from rest_framework import serializers
from .models import *

class PizzaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pizza
        fields = '__all__'

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'

class BeverageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beverage
        fields = '__all__'

class PizzaPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PizzaPrice
        fields = '__all__'
    
    # Ensure price is converted to float
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['price'] = float(data['price'])
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class StoreInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreInfo
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        extra_kwargs = {
            'status': {'required': False, 'default': 'pending'},
            'order_date': {'required': False, 'read_only': True},
            'estimated_delivery_time': {'required': False}
        }

    def validate(self, data):
        """Ensure required fields are present"""
        required_fields = ['user', 'delivery_address', 'contact_phone', 'total_price']
        for field in required_fields:
            if field not in data:
                raise serializers.ValidationError(f"{field} is required")
        return data
    
    def to_representation(self, instance):
        """Convert Decimal to float for JSON serialization"""
        data = super().to_representation(instance)
        data['total_price'] = float(data['total_price'])
        return data
    
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'