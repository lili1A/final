from django.contrib import admin
from .models import Product, Creator, Notification 
admin.site.register(Product)
admin.site.register(Creator)
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'message')