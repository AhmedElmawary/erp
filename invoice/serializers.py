from rest_framework import serializers
# from .models import SupplierInvoice
from client.models import Client
from status.models import Status
from payment.models import Payment


class SerializerCommonFields(serializers.Serializer):
    code = serializers.UUIDField(read_only=True)

    client = serializers.PrimaryKeyRelatedField(
        queryset= Client.objects.all()
    )
    status = serializers.PrimaryKeyRelatedField(
        queryset= Status.objects.all()
    )
    payment = serializers.PrimaryKeyRelatedField(
        queryset= Payment.objects.all()
    )
    delivery_date = serializers.DateTimeField()
    cost = serializers.FloatField()
    issued_at = serializers.DateTimeField(required=False)


class InvoiceCreateSerializer(SerializerCommonFields):
    def create(self, data):
        return Invoice.objects.create(**data)


class InvoiceGetSerializer(SerializerCommonFields):
    pass


class InvoiceListSerializer(SerializerCommonFields):
    pass
