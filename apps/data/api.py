from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Car, Person
from .serializers import CarSerializer, PersonSerializer


class SearchableModelViewSet(viewsets.ModelViewSet):
    """ModelViewSet with a case-insensitive `?search=` filter."""

    search_fields = ()
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.query_params.get('search', '').strip()
        if query and self.search_fields:
            condition = Q()
            for field in self.search_fields:
                condition |= Q(**{f'{field}__icontains': query})
            queryset = queryset.filter(condition)
        return queryset


class PersonViewSet(SearchableModelViewSet):
    """People registered in the database, used for face recognition."""

    queryset = Person.objects.all().order_by('-time_of_creation')
    serializer_class = PersonSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ('name', 'email', 'contact')


class CarViewSet(SearchableModelViewSet):
    """Cars registered in the database, matched by licence plate."""

    queryset = Car.objects.all().order_by('-time_of_creation')
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ('owner', 'number', 'brand')