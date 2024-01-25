from django.conf import settings
from django.contrib.auth.models import User
from drf_extra_fields.fields import Base64ImageField

from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from .messages import (
    REVIEW_CREATE_EXIST_ERR, USER_CREATE_EXIST_EMAIL_ERR,
    USER_CREATE_EXIST_NAME_ERR, USER_CREATE_ME_ERR
)
from .models import Follow, MyUsers
from food.models import Reciep


class ProfileSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели User."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MyUsers
        fields = '__all__'

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    def validate(self, data):
        if data.get('username') == settings.USER_INFO_URL_PATH:
            raise serializers.ValidationError(USER_CREATE_ME_ERR)
        return data


class ProfileCreateSerializer(UserCreateSerializer):
    """Сериалайзер для регистрации нового пользователя."""
    class Meta:
        model = MyUsers
        fields = tuple(MyUsers.REQUIRED_FIELDS) + (
            MyUsers.USERNAME,
            'password',
        )

    def validate(self, data):
        email_in_db = MyUsers.objects.filter(email=data.get('email'))
        username_in_db = MyUsers.objects.filter(username=data.get('username'))

        if data.get('username') == settings.USER_INFO_URL_PATH:
            raise serializers.ValidationError(USER_CREATE_ME_ERR)
        if email_in_db.exists():
            if username_in_db.exists():
                return data
            raise serializers.ValidationError(USER_CREATE_EXIST_EMAIL_ERR)
        else:
            if username_in_db.exists():
                raise serializers.ValidationError(USER_CREATE_EXIST_NAME_ERR)
            return data


class ProfileUpdateSerializer(serializers.Serializer):
    pass


class ProfileDeleteSerializer(serializers.Serializer):
    pass

'''
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create(**validated_data)
        MyUsers.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile = instance.profile
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        profile.save()
        return instance
'''


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(read_only=True, slug_field='username')
    following = serializers.SlugRelatedField(
        slug_field='username', queryset=MyUsers.objects.all()
    )
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
        serializer = LimitReciepsSerializer(recipes, many=True, read_only=True)
        return serializer.data


class LimitReciepsSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Reciep
        fields = '__all__'
