from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core import mail
from .models import PasswordResetOTP

User = get_user_model()

class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='oldpassword123'
        )
        self.forgot_url = reverse('forgot_password')
        self.reset_url = reverse('reset_password')

    def test_forgot_password_sends_email_and_creates_otp(self):
        response = self.client.post(self.forgot_url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Password Reset OTP', mail.outbox[0].subject)
        
        otp_count = PasswordResetOTP.objects.filter(user=self.user).count()
        self.assertEqual(otp_count, 1)

    def test_reset_password_with_valid_otp(self):
        otp_obj = PasswordResetOTP.generate_otp(self.user)
        
        response = self.client.post(self.reset_url, {
            'email': 'test@example.com',
            'otp': otp_obj.otp,
            'new_password': 'newpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))
        
        otp_obj.refresh_from_db()
        self.assertTrue(otp_obj.is_verified)

    def test_reset_password_with_invalid_otp(self):
        response = self.client.post(self.reset_url, {
            'email': 'test@example.com',
            'otp': '000000',
            'new_password': 'newpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

