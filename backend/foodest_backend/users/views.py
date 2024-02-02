from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .serializers import ProfileSerializer, FollowSerializer

from djoser.views import UserViewSet
from django.contrib.auth import get_user_model
from .models import Follow

User = get_user_model()


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    search_fields = ('username',)

    @action(
        detail=False,
        methods=('get', 'patch',),
        permission_classes=(AllowAny,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__username=user)
        pagination_pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pagination_pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)

        if request.method == 'POST':
            serializer = FollowSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            following = get_object_or_404(
                Follow, user=user, author=author
            )
            following.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
