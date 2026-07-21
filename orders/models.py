from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from products.models import Product, Size, ProductSizeStock
import uuid

def generate_order_number():
    return f"ORD-{uuid.uuid4().hex[:6].upper()}"

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )
    
    CITY_CHOICES = (
        ('Inside Dhaka', 'Inside Dhaka'),
        ('Outside Dhaka', 'Outside Dhaka'),
    )
    
    order_number = models.CharField(max_length=20, unique=True, editable=False, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, default='Customer')
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=50, choices=CITY_CHOICES, default='Inside Dhaka')
    
    payment_method = models.CharField(max_length=50, default="Cash on Delivery")
    sender_number = models.CharField(max_length=20, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = generate_order_number()
        
        if self.pk:
            old_order = Order.objects.get(pk=self.pk)
            if old_order.status != 'Cancelled' and self.status == 'Cancelled':
                for item in self.items.all():
                    if item.size:
                        size_name = item.size.strip()
                        size_stock = item.product.size_stocks.filter(size__name__iexact=size_name).first()
                        if size_stock:
                            size_stock.stock += item.quantity
                            size_stock.save()
                            item.product.update_total_stock()
                        else:
                            item.product.stock += item.quantity
                            item.product.save(update_fields=['stock'])
                    else:
                        item.product.stock += item.quantity
                        item.product.save(update_fields=['stock'])
                    item.product.sold_quantity -= item.quantity
                    item.product.save(update_fields=['sold_quantity'])
            elif old_order.status == 'Cancelled' and self.status != 'Cancelled':
                for item in self.items.all():
                    if item.size:
                        size_name = item.size.strip()
                        size_stock = item.product.size_stocks.filter(size__name__iexact=size_name).first()
                        if size_stock:
                            size_stock.stock = max(0, size_stock.stock - item.quantity)
                            size_stock.save()
                            item.product.update_total_stock()
                        else:
                            item.product.stock = max(0, item.product.stock - item.quantity)
                            item.product.save(update_fields=['stock'])
                    else:
                        item.product.stock = max(0, item.product.stock - item.quantity)
                        item.product.save(update_fields=['stock'])
                    item.product.sold_quantity += item.quantity
                    item.product.save(update_fields=['sold_quantity'])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} by {self.user.name if self.user else self.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    size = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not self.price and self.product:
            self.price = self.product.price
            
        if not self.purchase_price and self.product:
            self.purchase_price = self.product.purchase_price
            
        super().save(*args, **kwargs)
        
        # Deduct stock when item is first created
        if is_new and self.order.status != 'Cancelled':
            if self.size:
                size_name = self.size.strip()
                size_stock = self.product.size_stocks.filter(size__name__iexact=size_name).first()
                if not size_stock:
                    # If ProductSizeStock didn't exist for this size yet, create it
                    size_obj = Size.objects.filter(name__iexact=size_name).first()
                    if not size_obj:
                        size_obj = Size.objects.create(name=size_name.upper())
                    self.product.sizes.add(size_obj)
                    size_stock = ProductSizeStock.objects.create(
                        product=self.product,
                        size=size_obj,
                        stock=max(0, self.product.stock)
                    )
                
                size_stock.stock = max(0, size_stock.stock - self.quantity)
                size_stock.save()
                self.product.update_total_stock()
            else:
                self.product.stock = max(0, self.product.stock - self.quantity)
                self.product.save(update_fields=['stock'])

            self.product.sold_quantity += self.quantity
            self.product.save(update_fields=['sold_quantity'])

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Order {self.order.id}"

    def get_cost(self):
        return self.price * self.quantity

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s Cart"

    def get_cost(self):
        return self.product.price * self.quantity

class StoreSetting(models.Model):
    delivery_charge_inside_dhaka = models.DecimalField(max_digits=10, decimal_places=2, default=60.00)
    delivery_charge_outside_dhaka = models.DecimalField(max_digits=10, decimal_places=2, default=120.00)
    youtube_video_id = models.CharField(max_length=50, blank=True, null=True, default="7wtfhZwyrcc")
    bkash_number = models.CharField(max_length=20, blank=True, null=True)
    nagad_number = models.CharField(max_length=20, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk and StoreSetting.objects.exists():
            return StoreSetting.objects.first()
        return super().save(*args, **kwargs)
        
    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Store Settings"
