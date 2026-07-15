from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from products.serializers import ProductSerializer
from django.db import transaction
from .models import StoreSetting

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'product_name', 'price', 'quantity', 'size']
        read_only_fields = ['product']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'name', 'email', 'phone', 
            'address', 'city', 'payment_method', 'status', 
            'total_amount', 'delivery_charge', 'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ['order_number', 'status', 'total_amount', 'delivery_charge', 'created_at', 'updated_at', 'user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user and request.user.is_staff:
            if 'status' in self.fields:
                self.fields['status'].read_only = False

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # 1. Pre-check all items for stock
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Not enough stock for {product.name}. Available: {product.stock}"
                )
                
        # 2. Create Order
        order = Order.objects.create(**validated_data)
        # 3. Calculate delivery charge based on city
        settings = StoreSetting.get_settings()
        delivery_charge = settings.delivery_charge_inside_dhaka if order.city == 'Inside Dhaka' else settings.delivery_charge_outside_dhaka
        order.delivery_charge = delivery_charge
        
        total_amount = delivery_charge
        
        # 4. Create OrderItems
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = product.price # Price at time of purchase
            
            size = item_data.get('size', None)
            
            OrderItem.objects.create(
                order=order,
                product=product,
                price=price,
                quantity=quantity,
                size=size
            )
            
            total_amount += (price * quantity)
            
        # 5. Save total amount on Order
        order.total_amount = total_amount
        order.save()
        
        # 5. Clear user's cart if exists
        try:
            cart = Cart.objects.get(user=order.user)
            cart.items.all().delete()
        except Cart.DoesNotExist:
            pass
        
        return order

from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.ImageField(source='product.image_1', read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'product_image', 'quantity', 'total_price']
        
    def get_total_price(self, obj):
        return obj.get_cost()

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity')
        if product and quantity:
            if product.stock < quantity:
                raise serializers.ValidationError(f"Not enough stock. Available: {product.stock}")
        return data

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_amount', 'created_at']

    def get_total_amount(self, obj):
        return sum([item.get_cost() for item in obj.items.all()])

class StoreSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreSetting
        fields = ['delivery_charge_inside_dhaka', 'delivery_charge_outside_dhaka', 'updated_at']
