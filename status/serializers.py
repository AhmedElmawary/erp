from rest_framework import serializers
from django.db import IntegrityError
from .models import Status

class SerializerCommonFields(serializers.Serializer):
    name = serializers.CharField(required=True)

class StatusCreateSerializer(SerializerCommonFields):
    
    def create(self, data):
        return Status.objects.create(**data)


class StatusGetSerializer(SerializerCommonFields):
    pass

class StatusListSerializer(SerializerCommonFields):
    pass

