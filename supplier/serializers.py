from rest_framework import serializers
from .models import Supplier

class SupplierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


class SupplierRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


class SupplierCreateSerializer(serializers.Serializer):
    name                    =   serializers.CharField(required=True)
    is_active               =   serializers.CharField(default=True, required=False, read_only=True)
    img                     =   serializers.ImageField(required=False)
    email                   =   serializers.CharField(required=True)
    phone                   =   serializers.CharField(required=True)
    address                 =   serializers.CharField(required=True)
    city                    =   serializers.CharField(required=False)
    country                 =   serializers.CharField(required=True)
    is_company_owner        =   serializers.BooleanField(default=False)
    gender                  =   serializers.IntegerField(required=True)                  

    def create(self, data):
        return Supplier.objects.create(**data)
