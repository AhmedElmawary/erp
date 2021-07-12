from rest_framework import serializers
from .models import (
    Payment,
    )

from django.utils import timezone
from status.models import Status
from datetime import datetime


class PaymentCreateSerializer(serializers.Serializer):
    date = serializers.DateField(default=datetime.today)
    time = serializers.TimeField(default=timezone.localtime)
    status  = serializers.PrimaryKeyRelatedField(
        queryset= Status.objects.all()
    )
    amount = serializers.CharField()
    currency = serializers.IntegerField()

    def create(self, data):
        return Payment.objects.create(**data)


class PaymentListSerializer(serializers.Serializer):
    code        = serializers.UUIDField(read_only=True)
    date        = serializers.DateField(read_only=True)
    time        = serializers.TimeField(read_only=True)
    status      = serializers.StringRelatedField()
    amount      = serializers.CharField(read_only=True)
    currency    = serializers.CharField(read_only=True, source='get_currency')


class PaymentGetSerializer(PaymentListSerializer):
    
    pass



