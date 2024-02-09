from django_filters import rest_framework as filters

from .models import Reciep, Tags
from users.models import MyUsers


class RecipeFilter(filters.FilterSet):
    """Фильтрует выборку рецептов по полям."""

    author = filters.ModelMultipleChoiceFilter(
        field_name='author__id',
        to_field_name='id',
        queryset=MyUsers.objects.all()
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tags.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Reciep
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(cart__user=self.request.user)
        return queryset


class IngredientSearchFilter(filters.CharFilter):
    search_param = 'name'
