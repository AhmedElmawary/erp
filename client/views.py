from rest_framework.viewsets import GenericViewSet

from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin
    )

from .models import (Client)

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from .serializers import (
    ClientListSeriaizler,
    ClientRetrieveSerialzier,
    ClientCreateSerialzier,
    )
    
class InitCleint(GenericViewSet):
    queryset = Client.objects.all()
    # permissio n_classes = (IsAuthenticated,)
    # authentication_classes = (TokenAuthentication,)

class ClientList(InitCleint, ListModelMixin):
    serializer_class = ClientListSeriaizler

class ClientRetrieve(InitCleint, RetrieveModelMixin):
    serializer_class = ClientRetrieveSerialzier


class ClientCreate(InitCleint, CreateModelMixin):
    serializer_class = ClientCreateSerialzier
