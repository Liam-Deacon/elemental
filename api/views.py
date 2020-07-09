from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from django_filters import CharFilter
import django_filters.rest_framework as filters

from api.models import Element, Isotope
from api.serializers import ElementSerializer, IsotopeSerializer


class ElementViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Elements to be viewed or edited.
    """
    queryset = Element.objects.all()
    serializer_class = ElementSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ('name', 'symbol', 'atomic_number', 'period', 'group')


class IsotopeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Isotopes to be viewed or edited.
    """

    @staticmethod
    def get_element(query, value):
        return query.extra(where=['element = %s'], params=[value])

    queryset = Isotope.objects.all()
    serializer_class = IsotopeSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ('isotope', 'halflife', 'year_discovered')
    filter_fields = {
        'isotope': ['exact'],
        'halflife': ['exact'],
        'year_discovered': ['gte', 'lte', 'exact']
    }
    element = CharFilter(action=get_element)
