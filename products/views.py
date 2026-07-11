from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from .models import Category, Product, Review, Banner, InstagramImage
from .serializers import CategorySerializer, ProductSerializer, ReviewSerializer, BannerSerializer, InstagramImageSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.action == 'list':
            return Category.objects.filter(parent__isnull=True)
        return Category.objects.all()

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'category__slug', 'stock']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'sold_quantity']
    
    # To get top selling products, frontend can pass ?ordering=-sold_quantity

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user and user.is_authenticated and user.is_staff:
            return Review.objects.all().order_by('-created_at')
        return Review.objects.filter(status='approved').order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='pending')

class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.all().order_by('-created_at')
    serializer_class = BannerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated and self.request.user.is_staff:
            return Banner.objects.all().order_by('-created_at')
        return Banner.objects.filter(is_active=True).order_by('-created_at')

class InstagramImageViewSet(viewsets.ModelViewSet):
    queryset = InstagramImage.objects.all().order_by('-created_at')
    serializer_class = InstagramImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
