'''
A file that stores all REST API views.

'''

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer

from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication
from django.contrib.auth import authenticate,login

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

class LoginView(KnoxLoginView):
    serializer_class=AuthSerializer 
    permission_classes=(AllowAny,)

    def post(self,request,format=None):
        serializer=AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user= serializer.validated_data['user']
        login(request,user)       
        return super().post(request,format=None)

class ExampleView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)
    
