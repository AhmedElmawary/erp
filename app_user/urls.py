from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsersList,
    UserRetrieve,
    UserCreate,
    UserDelete,
    ChangeLanguage
    )


router = DefaultRouter()
router.register(prefix='list', viewset=UsersList, )
router.register(prefix='retrive', viewset=UserRetrieve, basename='user-retrive')
router.register(prefix='create', viewset=UserCreate,    basename='user-create')
router.register(prefix='delete', viewset=UserDelete,    basename='user-delete')



urlpatterns = [
    path('', include(router.urls)), 
]


# [print(url) for url in router.urls]