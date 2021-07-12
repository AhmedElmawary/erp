
from .views import (
    SupplierList,
    SupplierRetrieve,
    SupplierCreate,
    )
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(prefix='supplier/list',      viewset=SupplierList,      basename='supplier-list')
router.register(prefix='supplier/retrive',   viewset=SupplierRetrieve,  basename='supplier-retrive')
router.register(prefix='supplier/create',    viewset=SupplierCreate,    basename='supplier-create')

urlpatterns = [
    path('', include(router.urls))
]
