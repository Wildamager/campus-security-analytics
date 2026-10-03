from rest_framework import serializers

from .models import Car, Person


class PersonSerializer(serializers.ModelSerializer):
    # The photo can be uploaded later, so it stays optional on the API.
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Person
        fields = [
            'id',
            'name',
            'email',
            'contact',
            'image',
            'time_of_creation',
            'time_of_update',
        ]
        read_only_fields = ['time_of_creation', 'time_of_update']

    def validate_email(self, value):
        if not value:
            return value
        return value.strip().lower()


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = [
            'id',
            'owner',
            'number',
            'brand',
            'time_of_creation',
            'time_of_update',
        ]
        read_only_fields = ['time_of_creation', 'time_of_update']

    def validate_number(self, value):
        return value.replace(' ', '').upper()