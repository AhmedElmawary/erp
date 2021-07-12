from django.urls import path, include
from rest_framework.routers import DefaultRouter 
from .views import (
    PaymentCreate,
    PaymentGet,
    PaymentList,
    )

router = DefaultRouter()

urlpatterns = [
#Payment
    path("create/", PaymentCreate.as_view(), name="payment-create"),
    path("list/", PaymentList.as_view(), name="payment-list"),
    path("list/<int:pk>", PaymentGet.as_view(), name="payment-detail"),
    
]
