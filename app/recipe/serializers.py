from rest_framework import serializers
from core.models import Tag, Ingregient

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingregient
        fields = ('id', 'name')
        read_only_fields = ('id',)