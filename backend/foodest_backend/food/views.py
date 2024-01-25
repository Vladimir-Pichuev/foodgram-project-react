from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from .models import Reciep, Ingredients, Tags

from .serializers import (
    IngredientSerializer, TagSerializer, ReciepSerializerRead, ReciepSerializerWrite
)
from users.permissions import (
    IsAdminOrReadOnly, IsSuperUserOrAdmin, IsAuthorOrJustReading
)
from rest_framework.pagination import (
    LimitOffsetPagination, PageNumberPagination
)
from rest_framework import permissions


class IngredientViewSet(ModelViewSet ):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class ReciepViewSet(ModelViewSet):
    queryset = Reciep.objects.all()
    serializer_class = ReciepSerializerRead
    permission_classes = (IsAuthorOrJustReading, )
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ReciepSerializerRead
        return ReciepSerializerWrite
