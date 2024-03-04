from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'phoneNumber', 'email', 'linkedId', 'linkPrecedence', 'createdAt', 'updatedAt', 'is_deleted', 'deletedAt']
        read_only_fields = ['id','createdAt', 'updatedAt']