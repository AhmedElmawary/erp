from rest_framework.viewsets import GenericViewSet

from .serializers import (
    SupplierListSerializer,
    SupplierRetrieveSerializer,
    SupplierCreateSerializer
    )

from .models import (Supplier,)

from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin
    )


from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


class MainAuth():
    pass
    # permission_classes = (IsAuthenticated,)
    # authentication_classes = (TokenAuthentication,)

class InitSupplier(GenericViewSet):
    queryset = Supplier.objects.all()


class SupplierList(InitSupplier, ListModelMixin):
    serializer_class = SupplierListSerializer


class SupplierRetrieve(InitSupplier, RetrieveModelMixin):
    serializer_class = SupplierRetrieveSerializer


class SupplierCreate(InitSupplier, CreateModelMixin):
    serializer_class = SupplierCreateSerializer


# class SupplierDelete(InitSupplier, DestroyModelMixin):
    # pass