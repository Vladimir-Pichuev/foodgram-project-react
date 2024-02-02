'''class ProfileCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для регистрации нового пользователя."""
    # last_login = serializers.HiddenField(default=DateTimeField(auto_now_add = True))

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

    #def create(self, validated_data):
    #    user = MyUsers.objects.create(**validated_data)
    #    user.set_password(validated_data["password"])
    #    user.save()
    #    return user


# Вызов метода с использованием экземпляра
# print(ProfileCreateSerializer().get_all_fields())



class ProfileUpdateSerializer(serializers.Serializer):
    pass


class ProfileDeleteSerializer(serializers.Serializer):
    pass


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