from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.parent.name} -> {self.name}" if self.parent else self.name

class Size(models.Model):
    name = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    short_description = models.TextField(blank=True, help_text="Initial short details")
    description = models.TextField(blank=True)
    
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Main price (Auto Calculated)", blank=True)
    
    image_1 = models.ImageField(upload_to='products/')
    image_2 = models.ImageField(upload_to='products/', null=True, blank=True)
    image_3 = models.ImageField(upload_to='products/', null=True, blank=True)
    image_4 = models.ImageField(upload_to='products/', null=True, blank=True)
    image_5 = models.ImageField(upload_to='products/', null=True, blank=True)
    
    sizes = models.ManyToManyField(Size, blank=True, related_name='products')
    
    stock = models.IntegerField(default=0)
    sold_quantity = models.IntegerField(default=0, help_text="Used for top selling products filter")
    
    expire_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Auto calculate main price
        if self.offer_price:
            self.price = self.selling_price - self.offer_price
        else:
            self.price = self.selling_price
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Review(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} review for {self.product.name}"

class Banner(models.Model):
    badge_name = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True)
    button_1_text = models.CharField(max_length=100, blank=True)
    button_1_link = models.CharField(max_length=255, blank=True)
    button_2_text = models.CharField(max_length=100, blank=True)
    button_2_link = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='banners/', max_length=500)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class InstagramImage(models.Model):
    image = models.ImageField(upload_to='instagram/', max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Instagram Image {self.id}"
