from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.response import Response
from app_user.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils import translation
from django.shortcuts import redirect , reverse
from django.http import HttpResponseRedirect

from .serializers import (
    UserListSerialzier,
    UserRetrieveSerialzier,
    UserCreateSerializer,
    ChangLanguageSerialier
    )

class  InitUser(GenericViewSet):
    queryset = User.objects.all()
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    
class UsersList(
    InitUser,
    mixins.ListModelMixin
    ):
    serializer_class = UserListSerialzier


class UserRetrieve(
    InitUser,
    mixins.RetrieveModelMixin
    ):
    serializer_class = UserRetrieveSerialzier


class UserCreate(
    InitUser,
    mixins.CreateModelMixin
    ):
    authentication_classes = []
    permission_classes = []

    serializer_class = UserCreateSerializer

#TODO:: retireve error
class UserDelete(
    InitUser,
    mixins.RetrieveModelMixin
    ):
    pass


class ChangeLanguage(
    APIView
    ):
    serializer_class = ChangLanguageSerialier
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        # current_laguage = translation.get_language()

        serilized_data = self.serializer_class(data={"lang":request.data.get('lang')})
        serilized_data.is_valid(raise_exception=True)
        disered_language = serilized_data.data['lang']
        translation.activate(disered_language)
        request.session[translation.LANGUAGE_SESSION_KEY]= disered_language
        referer = request.META.get('HTTP_REFERER')
        referer_url = referer.split('/')
        referer_url[3] = disered_language 
        if not referer_url.count('admin') > 0:
            referer_url[3]+='/admin'
    
        url='/'.join(referer_url)
        return HttpResponseRedirect(url)