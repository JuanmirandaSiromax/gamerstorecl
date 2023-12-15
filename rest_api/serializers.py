from rest_framework import serializers
from mientretencion.models import Juego, Categoria

class JuegoSerializer(serializers.ModelSerializer):
    class Meta:
        model= Juego
        fields = ['id','codigo_invent','nombre','descripcion','imagen','categoria']

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model= Categoria
        fields = ['nombre']