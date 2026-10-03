from drf_spectacular.utils import extend_schema
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Camers, EntryCarLog, EntryPersonLog
from .serializers import (
    CameraSerializer,
    EntryCarLogSerializer,
    EntryPersonLogSerializer,
)


class CameraViewSet(viewsets.ModelViewSet):
    """Registered IP cameras. RTSS credentials are write-only."""

    queryset = Camers.objects.all().order_by('-time_of_creation')
    serializer_class = CameraSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']


class EntryPersonLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EntryPersonLog.objects.all().order_by('-date')
    serializer_class = EntryPersonLogSerializer
    permission_classes = [IsAuthenticated]


class EntryCarLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EntryCarLog.objects.all().order_by('-date')
    serializer_class = EntryCarLogSerializer
    permission_classes = [IsAuthenticated]


class DashboardSummarySerializer(serializers.Serializer):
    cameras = serializers.IntegerField()
    persons = serializers.IntegerField()
    cars = serializers.IntegerField()
    person_entries = serializers.IntegerField()
    car_entries = serializers.IntegerField()


class DashboardSummaryView(APIView):
    """Counts for the dashboard header."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses=DashboardSummarySerializer)
    def get(self, request):
        from ..data.models import Car, Person

        return Response({
            'cameras': Camers.objects.count(),
            'persons': Person.objects.count(),
            'cars': Car.objects.count(),
            'person_entries': EntryPersonLog.objects.count(),
            'car_entries': EntryCarLog.objects.count(),
        })