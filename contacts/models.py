from django.db import models

class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    
    # Admin reply field
    reply = models.TextField(blank=True, null=True, help_text="Write your reply here. An email will be sent to the user when you save.")
    replied_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject}"
