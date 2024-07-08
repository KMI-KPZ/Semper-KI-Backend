"""
Part of Semper-KI software

Akshay NS 2024

Contains: Exception Serializer
"""

from rest_framework import serializers

######################################################################
class ExceptionSerializer(serializers.Serializer):
    message = serializers.CharField()
    exception = serializers.CharField()