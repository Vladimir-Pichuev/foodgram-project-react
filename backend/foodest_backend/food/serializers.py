import base64
from rest_framework.serializers import (
    ModelSerializer,
    ImageField,
    HiddenField,
    CurrentUserDefault
)
from django.core.files.base import ContentFile

from .models import Ingredients, Tags, Reciep, IngredientInRecipe
from users.serializers import ProfileSerializer


class ListReciepSerializer(ModelSerializer):

    class Meta:
        model = Reciep
        fields = ('id', 'title')


class ReciepSerializer(ModelSerializer):
    author = ProfileSerializer(many=False)

    class Meta:
        model = Reciep
        fields = ('title', 'content')

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_all_fields(self):
        fields = list(self.fields.keys())
        return fields


class ReciepCreateSerializer(ModelSerializer):
    author = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Reciep
        fields = '__all__'

    def create(self, validated_data):
        """Создаёт новый рецепт."""
        ingredients_data = validated_data.pop('recipes_ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Reciep.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        ingredients_to_create = []
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data.get('ingredient')
            amount = ingredient_data.get('amount')
            ingredients_to_create.append(
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount
                )
            )
        IngredientInRecipe.objects.bulk_create(ingredients_to_create)
        return recipe


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'quantity')


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'color_code')


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)
