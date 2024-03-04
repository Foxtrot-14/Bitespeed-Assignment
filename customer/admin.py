from django.contrib import admin
from .models import Customer
# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'phoneNumber', 'email']
    list_filter = ['linkPrecedence', 'createdAt', 'updatedAt', 'is_deleted']
    search_fields = ['phoneNumber', 'email']
    readonly_fields = ['createdAt', 'updatedAt']