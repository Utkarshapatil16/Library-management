from rest_framework import serializers
from .models import Book,Issue

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model=Issue
        fields = '__all__'