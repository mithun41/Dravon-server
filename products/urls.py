from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ReviewViewSet, BannerViewSet, InstagramImageViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'banners', BannerViewSet)
router.register(r'instagram-images', InstagramImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
