import logging

from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework.viewsets import ModelViewSet
from .models import Reciep, Ingredients, Tags
from rest_framework import status

from .serializers import (
    IngredientSerializer,
    TagSerializer,
    ReciepSerializer,
    ReciepCreateSerializer,
    ListReciepSerializer
)
from users.permissions import (
    IsAdminOrReadOnly,
    IsAuthorOrJustReading
)
from rest_framework.pagination import (
    LimitOffsetPagination
)
from rest_framework import permissions


logger = logging.getLogger(__name__)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredients.objects.all().prefetch_related('tag')
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)


class TagViewSet(ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class ReciepViewSet(ModelViewSet):
    permission_classes = (IsAuthorOrJustReading, )
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        logger.debug('Queryset started')
        queryset = Reciep.objects.all().select_related(
            'author').prefetch_related()
        return queryset

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ReciepSerializer
        if self.action == 'list':
            return ListReciepSerializer
        return ReciepCreateSerializer

    def add_tags(self, request):
        tag_data = request.data.get('tag', {})
        reciep_id = request.data.get('reciep_id')

        # Получение объекта рецепта
        reciep = get_object_or_404(Reciep, id=reciep_id)

        # Создание или выбор существующего тега
        tag_serializer = TagSerializer(data=tag_data)
        tag_serializer.is_valid(raise_exception=True)
        tag = tag_serializer.save()

        # Добавление тега к рецепту
        reciep.tags.add(tag)
        reciep.save()

        # Сериализация рецепта и возвращение данных
        serializer = ReciepSerializer(reciep)
        return Response(serializer.data, status=status.HTTP_200_OK)
