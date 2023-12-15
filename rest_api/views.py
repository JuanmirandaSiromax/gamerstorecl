from django.shortcuts import render
from mientretencion.models import Juego
from .serializers import JuegoSerializer
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import requests

@csrf_exempt
@api_view(['GET', 'POST'])
#@permission_classes((IsAuthenticated,))
def listado_juegos_api(request):
    if request.method == 'GET':
        juego = Juego.objects.all()
        serializer = JuegoSerializer(juego, many=True)
    
        return Response(serializer.data)
    elif request.method == 'POST':
        data =JSONParser().parse(request)
        serializer = JuegoSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print('error', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['GET', 'PUT','PATCH','DELETE'])    
#@permission_classes((IsAuthenticated,))    
def vista_juegos_api(request, id):

    try:
        juego = Juego.objects.get(id=id)
    except Juego.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method =='GET':
        serializer = JuegoSerializer(juego)
        return Response(serializer.data)
    
    elif request.method =='PUT' or request.method =='PATCH':
        serializer = JuegoSerializer(juego, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            print('error', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method =='DELETE':
        juego.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@csrf_exempt
@api_view(['GET', 'PUT','PATCH','DELETE'])    
#@permission_classes((IsAuthenticated,))    
def detalle_juego_api(request):

        return render(request, 'juegos/detalle_juego.html')


@csrf_exempt
@api_view(['GET', 'PUT','PATCH','DELETE'])    
#@permission_classes((IsAuthenticated,)) 
def personajes_juego_api(request):

    return render(request, 'juegos/personajes_juego.html')