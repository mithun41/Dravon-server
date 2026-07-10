from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'phone_number', 'role', 'is_staff', 'is_active')
    search_fields = ('email', 'name', 'phone_number')
    ordering = ('email',)
