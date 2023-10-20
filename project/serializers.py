from .models import *
from rest_framework import serializers
 
 
class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Options
        # Поля, которые мы сериализуем
        fields = "__all__"
 
class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Applications
        # Поля, которые мы сериализуем
        fields = "__all__"
 
class ApplicationsoptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicationsoptions
        fields = '__all__'