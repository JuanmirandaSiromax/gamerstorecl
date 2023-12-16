from django.shortcuts import render
from mientretencion.models import Juego
from .serializers import JuegoSerializer
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token

@csrf_exempt
@api_view(['POST'])
def login(request):
    data=JSONParser().parse(request)

    username =data['username']
    password =data['password']

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response('Los Datos entregados no existen o son incorrecto')
    
    pass_valido = check_password(password, user.password)

    if not pass_valido:
        return Response('Password Incorrecto')
    
    token, created =Token.objects.get_or_create(user=user)
    return Response(token.key)