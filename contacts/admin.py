from django.contrib import admin
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'subject', 'created_at', 'is_replied')
    list_filter = ('created_at', )
    search_fields = ('first_name', 'last_name', 'email', 'subject')
    readonly_fields = ('first_name', 'last_name', 'email', 'subject', 'message', 'created_at', 'replied_at')

    def is_replied(self, obj):
        return bool(obj.replied_at)
    is_replied.boolean = True
    is_replied.short_description = 'Replied?'

    def save_model(self, request, obj, form, change):
        if change and obj.reply and 'reply' in form.changed_data:
            obj.replied_at = timezone.now()
            # Attempt to send an email to the user
            try:
                send_mail(
                    subject=f"Re: {obj.subject}",
                    message=obj.reply,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'admin@example.com'),
                    recipient_list=[obj.email],
                    fail_silently=True,
                )
            except Exception as e:
                # If email fails (e.g. backend not configured), we still save the reply
                print(f"Failed to send reply email: {e}")
                
        super().save_model(request, obj, form, change)
