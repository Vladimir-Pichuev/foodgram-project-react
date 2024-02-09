from rest_framework import serializers, status

from .models import (
    Reciep,
    IngredientInRecipe,
    Ingredients,
    Tags,
    Favourite,
    ShoppingCart
)

import base64
import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """
    Добавление изображений к рецептам кодируя в base64
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class Hex2NameColor(serializers.Field):
    """
    Добавление цвета при создании тега
    #ffff00 - желтый
    #00ff00 - зеленый
    #ff0000 - красный
    """

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError("Для этого цвета нет имени")
        return data


class RecipeProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов в профиле пользователя."""

    class Meta:
        model = Reciep
        fields = ('id', 'title', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для просмотра тегов."""
    color_code = Hex2NameColor()

    class Meta:
        model = Tags
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для просмотра ингредиентов."""
    id = serializers.ReadOnlyField()
    ingredients_name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = Ingredients
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для связной модели RecipeIngredient"""
    id = serializers.IntegerField(source='ingredients.id')
    ingredients_name = serializers.ReadOnlyField(
        source='ingredients.ingredients_name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'recipe',
            'ingredient',
            'amount',
            'measurement_unit',
            'ingredients_name'
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='ingredient_list')
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reciep
        fields = '__all__'

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.cart.filter(recipe=obj).exists()


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tags.objects.all(),
        required=True)

    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Reciep
        fields = '__all__'
        read_only_fields = ('author',)

    def validate_ingredients(self, value):
        if not all(ingredient['amount'] for ingredient in value):
            raise serializers.ValidationError(
                'Количество ингредиента не может быть равным нулю'
            )
        return value

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 1 мин.')
        return cooking_time

    def create_ingredients(self, ingredients, recipe):
        IngredientInRecipe.objects.bulk_create([IngredientInRecipe(
            recipe=recipe,
            ingredient_id=ingredient['ingredient']['id'],
            amount=ingredient.get('amount')) for ingredient in ingredients
        ])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Reciep.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data


class FavoritRecipeSerializer(RecipeSerializer):

    class Meta:
        model = Reciep
        fields = ('id', 'title', 'cooking_time', 'image')
        read_only_fields = ('title', 'cooking_time', 'image')

    def validate(self, data):
        recipe = self.instance
        user = self.context.get('request').user
        if Favourite.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже в избранных',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


class CartSerializer(RecipeSerializer):
    """Сериализатор добавления рецепта в корзину"""

    class Meta(RecipeSerializer.Meta):
        fields = ('id', 'title', 'image', 'cooking_time')
        read_only_fields = ('title', 'cooking_time', 'image')

    def validate(self, data):
        recipe = self.instance
        user = self.context.get('request').user
        if ShoppingCart.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже в корзине',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data
