from .models import *
from rest_framework import serializers
from collections import OrderedDict
 
class UserSerializer(serializers.ModelSerializer):
    is_moderator = serializers.BooleanField(default=False, required=False)
    class Meta:
        model = Users
        fields = ['email', 'password', 'is_moderator'] 

class UserAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['email'] 

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Options
        # Поля, которые мы сериализуем
        fields = "__all__"
 
class ApplicationSerializer(serializers.ModelSerializer):
    customer = UserAppSerializer(read_only=True)
    class Meta:
        # Модель, которую мы сериализуем
        model = Applications
        # Поля, которые мы сериализуем
        fields = "__all__"
        
 
class ApplicationsoptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicationsoptions
        fields = '__all__'