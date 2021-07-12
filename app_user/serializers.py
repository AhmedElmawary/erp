from rest_framework import serializers
from app_user.models import User

class UserListSerialzier(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = "__all__"
        extra_kwargs = {
            'password': {'write_only': True}
        } 

class UserRetrieveSerialzier(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            'password': {'write_only': True}
        } 


class UserCreateSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True,)
    first = serializers.CharField(required=True,)
    last = serializers.CharField(required=True,)
    age = serializers.IntegerField(required=True,)
    address = serializers.CharField(required=True,)
    gender = serializers.IntegerField(required=True,)
    email = serializers.CharField(required=True,)
    country = serializers.CharField(required=True,)
    password = serializers.CharField(required=True, write_only=True)
    city = serializers.CharField(required=False,)


    def validate_age(self, age):
        if age < 6 or len(str(age)) > 3:
            raise ValueError(f'user\'s age cann\'t be {age}') 

        return age

    def create(self, args):
        return User.objects.create(**self.validated_data)
        


class ChangLanguageSerialier(serializers.Serializer):
    lang = serializers.CharField(required=True, error_messages={'lang':'something went wrong'})

    