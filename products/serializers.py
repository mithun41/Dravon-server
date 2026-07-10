from rest_framework import serializers
from .models import Category, Product, Review

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
    reviews = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    def get_reviews(self, obj):
        approved_reviews = obj.reviews.filter(status='approved')
        return ReviewSerializer(approved_reviews, many=True).data

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_id', 'name', 'slug', 'description',
            'purchase_price', 'selling_price', 'offer_price', 'price',
            'image_1', 'image_2', 'image_3', 'stock', 'sold_quantity',
            'expire_date', 'created_at', 'updated_at', 'reviews', 'average_rating'
        ]
        read_only_fields = ['price']

    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(status='approved')
        if reviews.exists():
            return sum([r.rating for r in reviews]) / reviews.count()
        return 0
