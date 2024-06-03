from django.contrib import admin
from .models import User, FriendRequest

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_admin', 'is_active')
    search_fields = ('email', 'name')
    list_filter = ('is_admin', 'is_active')
    ordering = ('email',)

class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status', 'created_at')
    search_fields = ('from_user__email', 'to_user__email')
    list_filter = ('status',)
    ordering = ('created_at',)

# Register your models with custom admin classes
admin.site.register(User, UserAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)