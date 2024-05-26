from rest_framework import viewsets
from rest_framework.decorators import action
from .models import Category, Event
from .serializers import CategorySerializer, EventSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ['title']


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filterset_fields = ['category', 'title']

    @action(methods=['post'], detail=True)
    def other_action(self, request, pk=None):
        pass
