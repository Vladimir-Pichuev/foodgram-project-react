from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.formats import date_format
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from users.permissions import IsAuthorOrJustReading
from users.models import MyUsers

from .filters import RecipeFilter
from .models import (
    Reciep,
    IngredientInRecipe,
    Ingredients,
    Tags,
    Favourite,
    ShopingList,
    ShoppingCart
)
from .pagination import Pagination
from .serializers import (
    CartSerializer,
    FavoritRecipeSerializer,
    IngredientSerializer,
    RecipePostSerializer,
    RecipeSerializer,
    TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Reciep.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = Pagination
    permission_classes = (IsAuthorOrJustReading,)
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filterset_class = RecipeFilter
    ordering = ('-id',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return RecipePostSerializer
        return RecipeSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, **kwargs):
        user = get_object_or_404(MyUsers, username=request.user)
        recipe = get_object_or_404(Reciep, id=self.kwargs.get('pk'))

        if request.method == 'POST':
            serializer = FavoritRecipeSerializer(
                recipe, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            Favourite.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite_recipe = get_object_or_404(
            Favourite, user=user, recipe=recipe
        )
        favorite_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        user = get_object_or_404(MyUsers, username=request.user)
        recipe = get_object_or_404(Reciep, id=self.kwargs.get('pk'))

        if request.method == 'POST':
            serializer = CartSerializer(
                recipe, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        cart_recipe = get_object_or_404(
            ShoppingCart, user=user, recipe=recipe
        )
        cart_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        if not user.cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = (
            IngredientInRecipe.objects.filter(
                recipe__cart__user=user
            )
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(sum_amount=Sum('amount')).order_by()
        )

        today = date_format(timezone.now(), use_l10n=True)
        headline = (
            f'Дата: {today} \n\n'
            f'Список покупок: \n\n'
        )
        lines = []
        for ingredient in ingredients:
            line = (
                f'➤ {ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]})'
                f' -- {ingredient["sum_amount"]}'
            )
            lines.append(line)

        shopping_list = headline + '\n'.join(lines)
        filename = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
