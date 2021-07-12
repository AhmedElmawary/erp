from rest_framework import serializers
from .models import (
    Client
) 



class ClientListSeriaizler(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__" 


class ClientRetrieveSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__" 


class ClientCreateSerialzier(serializers.Serializer):
    name                    =   serializers.CharField(required=True)
    gender                  =   serializers.IntegerField(required=True)                  
    is_active               =   serializers.CharField(default=True, required=False, read_only=True)
    img                     =   serializers.ImageField(required=False)
    email                   =   serializers.CharField(required=True)
    phone                   =   serializers.CharField(required=True)
    address                 =   serializers.CharField(required=True)
    city                    =   serializers.CharField(required=False)
    country                 =   serializers.CharField(required=True)

    def create(self, data):
        return Client.objects.create(**data)
