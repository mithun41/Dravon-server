from rest_framework import generics, permissions, filters
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .serializers import UserRegistrationSerializer, UserSerializer, ChangePasswordSerializer, ForgotPasswordSerializer, ResetPasswordSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = UserSerializer
    pagination_class = UserPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'name', 'phone_number']
    ordering_fields = ['date_joined', 'email', 'name']

from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        examples=[
            OpenApiExample(
                'Default Login',
                summary='Default Admin Login',
                value={
                    'email': 'mithun@gmail.com',
                    'password': '1234'
                },
                request_only=True,
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

from rest_framework.response import Response
from rest_framework import status

class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetOTP

class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Generate OTP
        otp_obj = PasswordResetOTP.generate_otp(user)
        
        # Send Email
        subject = 'Password Reset OTP - Dravon'
        message = f'Your Dravon Password Reset OTP code is: {otp_obj.otp}.\nThis OTP is valid for 10 minutes.'
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@dravon.com')
        
        send_mail(subject, message, from_email, [email], fail_silently=False)
        
        return Response({"message": "OTP has been sent to your email."}, status=status.HTTP_200_OK)

class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        otp_obj = serializer.validated_data['otp_obj']
        
        # Update password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Mark OTP as verified
        otp_obj.is_verified = True
        otp_obj.save()
        
        return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from orders.models import Order
from django.db.models import Count

class CustomerDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # 1. User Profile
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone_number": user.phone_number,
            "profile_pic": request.build_absolute_uri(user.profile_pic.url) if user.profile_pic else None
        }
        
        # 2. Order Statistics
        orders = Order.objects.filter(user=user)
        total_orders = orders.count()
        
        status_counts = orders.values('status').annotate(count=Count('status'))
        order_summary = {
            "total_orders": total_orders,
            "pending": 0,
            "processing": 0,
            "shipped": 0,
            "delivered": 0,
            "cancelled": 0
        }
        for item in status_counts:
            status = item['status'].lower()
            if status in order_summary:
                order_summary[status] = item['count']
                
        # 3. Recent Orders
        recent_orders = orders.order_by('-created_at')[:5]
        recent_orders_data = [
            {
                "order_number": o.order_number,
                "status": o.status,
                "total_amount": o.total_amount,
                "created_at": o.created_at
            } for o in recent_orders
        ]
        
        return Response({
            "user": user_data,
            "order_summary": order_summary,
            "recent_orders": recent_orders_data
        })
