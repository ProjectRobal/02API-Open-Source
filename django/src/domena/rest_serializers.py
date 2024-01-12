from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer


class UserUUID(serializers.Serializer):
    '''get optional uuid'''
    uuid=serializers.CharField(max_length=36,allow_blank=True)

class UserSerializer(serializers.Serializer):
    '''serialize for the 02 user object'''
    username=serializers.CharField()
    first_name=serializers.CharField()
    last_name=serializers.CharField()
    email=serializers.EmailField()


class UserRegisterSerializer(serializers.Serializer):
    '''serialize for registration the 02 user object'''
    username=serializers.CharField()
    first_name=serializers.CharField(allow_blank=True)
    last_name=serializers.CharField(allow_blank=True)
    email=serializers.EmailField()
    password=serializers.CharField()

class UserPermissionSerializer(serializers.Serializer):
    '''serialize for the 02 user object'''
    name=serializers.CharField()
    codename=serializers.CharField(max_length=100)

class AuthSerializer(serializers.Serializer):
    '''serialize for the user object'''
    username=serializers.CharField()
    password=serializers.CharField(
        style={'input_type':'password'},
        trim_whitespace=False
    )
    def validate(self,attrs):
        username= attrs.get('username')
        password= attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )

        if user is None:
            raise serializers.ValidationError(("Unable to authencticate user with credentials"),code='authentication')
        
        attrs['user'] = user