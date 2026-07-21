from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_number', 'user', 'name', 'payment_method', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'name', 'email', 'phone', 'sender_number', 'transaction_id', 'user__name', 'user__email']
    inlines = [OrderItemInline]
    readonly_fields = ['total_amount']
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'name', 'email', 'phone', 'address', 'city', 'status')
        }),
        ('Payment Info', {
            'fields': ('payment_method', 'sender_number', 'transaction_id', 'total_amount', 'delivery_charge')
        }),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Calculate total amount after items are saved
        total = sum([item.price * item.quantity for item in form.instance.items.all() if item.price])
        form.instance.total_amount = total
        form.instance.save()

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    inlines = [CartItemInline]
