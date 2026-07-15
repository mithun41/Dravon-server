from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, UserProfileView, UserListView, CustomTokenObtainPairView, ChangePasswordView, ForgotPasswordView, ResetPasswordView, CustomerDashboardView

urlpatterns = [
    path('', UserListView.as_view(), name='user_list'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('customer/dashboard/', CustomerDashboardView.as_view(), name='customer_dashboard'),
]
