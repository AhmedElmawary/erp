from django.urls import path, include
from rest_framework.routers import DefaultRouter 
from .views import (
    StatusCreate,
    StatusGet,
    StatusList
    )

router = DefaultRouter()

urlpatterns = [
    path("create/", StatusCreate.as_view(), name="status-create"),
    path("list/", StatusList.as_view(), name="status-list"),
    path("list/<int:pk>/", StatusGet.as_view(), name="status-detail"),
]
