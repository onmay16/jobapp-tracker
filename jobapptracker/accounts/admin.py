from django.contrib import admin

from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'phone', 'first_name', 'last_name', 'is_active',)
    list_filter = ('is_active',)
    search_fields = ('email', 'first_name', 'last_name')

admin.site.register(User, UserAdmin)