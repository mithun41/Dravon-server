from rest_framework import serializers
from .models import Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'email', 'subject', 'message', 'reply', 'replied_at', 'created_at']
        read_only_fields = ['reply', 'replied_at', 'created_at']
