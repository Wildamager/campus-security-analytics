from rest_framework import serializers

from .models import Camers, EntryCarLog, EntryPersonLog


class CameraSerializer(serializers.ModelSerializer):
    # RTSS credentials are accepted on write but never returned in a response.
    login = serializers.CharField(required=False, allow_blank=True, write_only=True)
    password = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Camers
        fields = [
            'id',
            'location',
            'ip',
            'port',
            'login',
            'password',
            'time_of_creation',
        ]
        read_only_fields = ['time_of_creation']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['has_credentials'] = bool(instance.login or instance.password)
        return representation


class EntryPersonLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryPersonLog
        fields = ['id', 'date', 'location', 'name']


class EntryCarLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryCarLog
        fields = ['id', 'date', 'location', 'number']