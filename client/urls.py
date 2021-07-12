from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ClientList, 
    ClientRetrieve,
    ClientCreate,
)

router = DefaultRouter()

router.register(prefix='client/list',      viewset=ClientList,      basename='client-list')
router.register(prefix='client/retrive',   viewset=ClientRetrieve,  basename='client-retrive')
router.register(prefix='client/create',    viewset=ClientCreate,    basename='client-create')

urlpatterns = [
    path('', include(router.urls))
]
