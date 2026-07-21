from rest_framework import serializers
from .models import Category, Product, Review, Banner, InstagramImage, Size, ProductSizeStock

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']

class ProductSizeStockSerializer(serializers.ModelSerializer):
    size_name = serializers.CharField(source='size.name', read_only=True)

    class Meta:
        model = ProductSizeStock
        fields = ['id', 'size', 'size_name', 'stock']

class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'parent', 'subcategories']
        
    def get_subcategories(self, obj):
        # Recursively serialize subcategories
        if obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.all(), many=True).data
        return []

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True
    )

    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'product_name', 'rating', 'comment', 'status', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', required=False, allow_null=True
    )
    sizes = SizeSerializer(many=True, read_only=True)
    size_stocks = ProductSizeStockSerializer(many=True, read_only=True)
    size_names = serializers.CharField(write_only=True, required=False, allow_blank=True)
    reviews = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    def get_reviews(self, obj):
        approved_reviews = obj.reviews.filter(status='approved')
        return ReviewSerializer(approved_reviews, many=True).data

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_id', 'name', 'slug', 'short_description', 'description',
            'purchase_price', 'selling_price', 'offer_price', 'price',
            'image_1', 'image_2', 'image_3', 'image_4', 'image_5', 'stock', 'sold_quantity',
            'sizes', 'size_stocks', 'size_names', 'expire_date', 'created_at', 'updated_at', 'reviews', 'average_rating'
        ]
        read_only_fields = ['price']
        
    def create(self, validated_data):
        size_names = validated_data.pop('size_names', None)
        product = super().create(validated_data)
        if size_names is not None:
            self._set_sizes(product, size_names)
        return product

    def update(self, instance, validated_data):
        size_names = validated_data.pop('size_names', None)
        product = super().update(instance, validated_data)
        if size_names is not None:
            self._set_sizes(product, size_names)
        return product

    def _set_sizes(self, product, size_names_str):
        if not size_names_str.strip():
            product.sizes.clear()
            product.size_stocks.all().delete()
            return
            
        tokens = [n.strip() for n in size_names_str.split(',') if n.strip()]
        size_objs = []
        
        # Track valid sizes to clear old removed sizes
        valid_size_ids = set()

        for token in tokens:
            has_explicit_stock = ':' in token
            if has_explicit_stock:
                parts = token.split(':')
                name = parts[0].strip().upper()
                try:
                    stock_qty = int(parts[1].strip())
                except ValueError:
                    stock_qty = 0
            else:
                name = token.strip().upper()
                stock_qty = 0

            size_obj, _ = Size.objects.get_or_create(name=name)
            size_objs.append(size_obj)
            valid_size_ids.add(size_obj.id)

            size_stock_obj, created = ProductSizeStock.objects.get_or_create(
                product=product, size=size_obj,
                defaults={'stock': stock_qty}
            )
            if has_explicit_stock:
                size_stock_obj.stock = stock_qty
                size_stock_obj.save()

        product.sizes.set(size_objs)
        # Delete size stocks for sizes no longer selected
        product.size_stocks.exclude(size_id__in=valid_size_ids).delete()
        product.update_total_stock()

    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(status='approved')
        if reviews.exists():
            return sum([r.rating for r in reviews]) / reviews.count()
        return 0

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

class InstagramImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstagramImage
        fields = '__all__'
