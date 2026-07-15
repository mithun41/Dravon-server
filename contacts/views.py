from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema_view, extend_schema
from .models import Contact
from .serializers import ContactSerializer

@extend_schema_view(
    list=extend_schema(tags=['contacts']),
    retrieve=extend_schema(tags=['contacts']),
    create=extend_schema(tags=['contacts']),
    update=extend_schema(tags=['contacts']),
    partial_update=extend_schema(tags=['contacts']),
    destroy=extend_schema(tags=['contacts']),
)
class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all().order_by('-created_at')
    serializer_class = ContactSerializer

    def get_permissions(self):
        if self.action == 'create':
            # Anyone can submit a contact form
            return [permissions.AllowAny()]
        # Only admin can view/edit/delete
        return [permissions.IsAdminUser()]
