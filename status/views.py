import rest_framework
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import (IsAuthenticated, IsAdminUser)
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED)
from rest_framework.response import Response
from .serializers import (
    StatusCreateSerializer,
    StatusGetSerializer,
    StatusListSerializer,
)

from typing import Dict

from .models import Status

class MainAuth:
    pass
    # authentication_classes = (TokenAuthentication, )
    # permission_classes     =   (IsAuthenticated,)

class InitStatus(MainAuth, APIView):
    queryset = Status.objects.filter()

# Trying to start code as strict code
class StatusCreate(InitStatus):
    serializer_class: rest_framework.serializers.Serializer = StatusCreateSerializer

    def post(self, request, format=None):
        serialized = self.serializer_class(data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save()

        return Response(serialized.data, HTTP_201_CREATED)

class StatusGet(InitStatus):
    serializer_class = StatusGetSerializer

    def get(self, request, pk):
        serilaized =  self.serializer_class(get_object_or_404(self.queryset, pk= pk))
        
        return Response(serilaized.data, HTTP_200_OK)


class StatusList(InitStatus):
    serializer_class = StatusListSerializer

    def get(self, request):
        serialized = self.serializer_class(get_list_or_404(self.queryset), many=True)
        
        return Response(serialized.data, HTTP_200_OK)
