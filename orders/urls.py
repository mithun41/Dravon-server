from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CartView, CartItemViewSet, DashboardStatsView, SalesReportView, StoreSettingView, TrackOrderView

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart/items', CartItemViewSet, basename='cart-items')

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('reports/sales/', SalesReportView.as_view(), name='sales-report'),
    path('settings/', StoreSettingView.as_view(), name='store-settings'),
    path('track-order/', TrackOrderView.as_view(), name='track-order'),
    path('', include(router.urls)),
]
