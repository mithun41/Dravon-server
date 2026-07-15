from rest_framework import serializers
from .models import Contact
from django.utils import timezone

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'email', 'subject', 'message', 'reply', 'replied_at', 'status', 'created_at']
        read_only_fields = ['first_name', 'last_name', 'email', 'subject', 'message', 'replied_at', 'created_at']

    def update(self, instance, validated_data):
        if 'reply' in validated_data and validated_data['reply'] != instance.reply:
            instance.replied_at = timezone.now()
            if instance.status == 'pending':
                instance.status = 'replied'
        return super().update(instance, validated_data)
