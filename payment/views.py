import rest_framework
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import (IsAuthenticated, IsAdminUser)
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED)
from rest_framework.response import Response
from .serializers import (
    PaymentCreateSerializer,
    PaymentGetSerializer,
    PaymentListSerializer,

)
from .models import (
    Payment,
    )


class MainAuth:
    pass
    # authentication_classes = (TokenAuthentication, )
    # permission_classes     =   (IsAuthenticated,)

class InitPayment(MainAuth, APIView):
    queryset = Payment.objects.filter()

# Trying to start code as strict code
class PaymentCreate(InitPayment):
    serializer_class: rest_framework.serializers.Serializer = PaymentCreateSerializer

    def post(self, request, format=None):
        serialized = self.serializer_class(data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save()

        return Response(serialized.data, HTTP_201_CREATED)

class PaymentGet(InitPayment):
    serializer_class = PaymentGetSerializer
    def get(self, request, pk):
        serilaized =  self.serializer_class(get_object_or_404(self.queryset, pk=pk))
        
        return Response(serilaized.data, HTTP_200_OK)


class PaymentList(InitPayment):
    serializer_class = PaymentListSerializer

    def get(self, request):
        serialized = self.serializer_class(get_list_or_404(self.queryset), many=True)
        
        return Response(serialized.data, HTTP_200_OK)

