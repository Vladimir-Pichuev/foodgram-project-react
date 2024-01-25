from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.shortcuts import render

from rest_framework.pagination import (
    LimitOffsetPagination, PageNumberPagination
)
from rest_framework.decorators import action
from rest_framework import (
    filters, mixins, permissions, status, viewsets
)
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from .filters import MyUsersFilter
from .serializers import (
    ProfileSerializer, ProfileCreateSerializer, ProfileUpdateSerializer,
    ProfileDeleteSerializer, FollowSerializer
)

from .permissions import (
    IsAdminOrReadOnly, IsAuthorOrJustReading, IsSuperUserOrAdmin
)

User = get_user_model()


class MyUsers(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthorOrJustReading,)
    pagination_class = LimitOffsetPagination
    search_fields = ('username',)

    @action(
        detail=False,
        methods=('get', 'patch',),
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role, partial=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class Follower(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['user__username', 'following__username']

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)