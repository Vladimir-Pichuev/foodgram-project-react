from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from .models import Follow, MyUsers
from food.models import Reciep

from drf_extra_fields.fields import Base64ImageField

FIELDS = (
    'id',
    'email',
    'username',
    'first_name',
    'last_name',
    'password',
)


class ProfileSerializer(UserSerializer):
    """Сериалайзер для модели User."""
    username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MyUsers
        fields = FIELDS

    def get_username(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return None
        return user.username

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()


class ProfileCreateSerializer(UserCreateSerializer):
    class Meta:
        model = MyUsers
        fields = FIELDS


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Reciep
        fields = ("id", "name", "image", "cooking_time")


class FollowSerializer(ProfileSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = '__all__'

    def validate_following(self, following):
        user = self.context['request'].user
        if user == following:
            raise serializers.ValidationError(
                'Вы не можете подписаться сами на себя.'
            )
        if Follow.objects.filter(user=user, following=following).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого человека.'
            )
        return following

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data


'''
class LimitReciepsSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Reciep
        fields = '__all__'
'''
