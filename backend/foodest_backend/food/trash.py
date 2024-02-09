class ListReciepSerializer(ModelSerializer):
    """Получаем список рецептов."""

    class Meta:
        model = Reciep
        fields = ('id', 'title')


class ReciepSerializer(ModelSerializer):
    """Получаем конкретный рецепт."""
    author = ProfileSerializer(many=False)

    class Meta:
        model = Reciep
        fields = ('title', 'content', 'author', 'ingredients')

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_all_fields(self):
        fields = list(self.fields.keys())
        return fields


class ReciepCreateSerializer(ModelSerializer):
    """Создаём рецепт."""
    author = HiddenField(default=CurrentUserDefault())
    ingredients = IngredientInRecipe()

    class Meta:
        model = Reciep
        fields = '__all__'

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise ValidationError(
                'Время готовки не может быть меньше минуты')
        return cooking_time

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError({
                'ingredients': 'Нужен хоть один ингридиент для рецепта'})

        tags = self.initial_data.get('tags')
        if not tags:
            raise ValidationError('Не указаны тэги')

        if len(data['tags']) > len(set(data['tags'])):
            raise ValidationError('Теги не могут повторяться!')

        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(Ingredients,
                                           id=ingredient_item['id'])
            if ingredient in ingredient_list:
                raise ValidationError('Ингридиенты должны '
                                      'быть уникальными')
            ingredient_list.append(ingredient)
            if int(ingredient_item['amount']) < 0:
                raise ValidationError({
                    'ingredients': ('Убедитесь, что значение количества '
                                    'ингредиента больше 0')
                })
        data['ingredients'] = ingredients
        return data

    def create_ingredients(self, ingredients, recipe):
        """ Метод создает рецепт с ингридиентами. """
        IngredientInRecipe.objects.bulk_create(
            IngredientInRecipe(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),)
            for ingredient in ingredients
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Reciep.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.set(tags)
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        self.create_ingredients(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ReciepSerializer(instance, context=context).data


class IngredientSerializer(ModelSerializer):
    """Получаем список ингридиентов."""
    id = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Ingredients
        fields = ('id', 'ingredients_name', 'quantity')
        read_only_fields = ('id', 'ingredients_name', 'quantity')


class TagSerializer(ModelSerializer):
    """Получаем список тегов."""
    class Meta:
        model = Tags
        fields = ('id', 'title', 'color_code', 'slug')

    def create(self, validated_data):
        title = validated_data.get('title')
        slug = slugify(title)
        validated_data['slug'] = slug
        return super().create(validated_data)


class Base64ImageField(ImageField):
    """Обработка изображений в формате base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)



class IngredientSerializer(ModelSerializer):
    """ Сериализатор  для модели Ingredient. """
    id = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Ingredients
        fields = '__all__'


class IngredientRecipeGetSerializer(ModelSerializer):
    """ Сериализатор для модели IngredientRecipe при GET запросах. """

    id = IntegerField(source='ingredient.id')
    name = CharField(source='ingredient.ingredient')
    measurement_unit = CharField(
        source='ingredient.amount'
    )

    class Meta:
        model = IngredientInRecipe
        fields = '__all__'


class IngredientRecipeSerializer(ModelSerializer):
    """ Сериализатор для модели IngredientRecipe при небезопасных запросах."""

    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = '__all__'


class TagSerializer(ModelSerializer):
    """ Сериализатор для модели Tag."""
    id = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Tags
        fields = '__all__'
        read_only_fields = ('slug',)

    def create(self, validated_data):
        title = validated_data.get('title')
        slug = slugify(title)
        validated_data['slug'] = slug
        return super().create(validated_data)


class RecipeGetSerializer(ModelSerializer):
    """ Сериализатор для модели Recipe при GET запросах."""
    tags = TagSerializer(many=True, read_only=True)
    author = HiddenField(default=CurrentUserDefault())
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = IngredientRecipeGetSerializer(
        many=True, source='amount_ingredients'
    )
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Reciep
        fields = '__all__'

    def get_is_favorited(self, obj):
        """Метод для поля is_favorited."""
        user = self.context.get('request').user
        return (user.is_authenticated
                and user.favorites.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        """Метод для поля is_in_shopping_cart."""
        user = self.context.get('request').user
        return (user.is_authenticated
                and user.cart.filter(recipe=obj).exists())


class RecipeCreateSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True
    )
    author = HiddenField(default=CurrentUserDefault())
    ingredients = IngredientRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Reciep
        fields = '__all__'

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise ValidationError(
                'Время готовки не может быть меньше минуты')
        return cooking_time

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError({
                'ingredients': 'Нужен хоть один ингридиент для рецепта'})

        tags = self.initial_data.get('tags')
        if not tags:
            raise ValidationError('Не указаны тэги')

        if len(data['tags']) > len(set(data['tags'])):
            raise ValidationError('Теги не могут повторяться!')

        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(Ingredients,
                                           id=ingredient_item['id'])
            if ingredient in ingredient_list:
                raise ValidationError(
                    'Ингридиенты должны быть уникальными'
                )
            ingredient_list.append(ingredient)
            if int(ingredient_item['amount']) < 0:
                raise ValidationError({
                    'ingredients': ('Убедитесь, что значение количества '
                                    'ингредиента больше 0')
                })
        data['ingredients'] = ingredients
        return data

    def create_ingredients_amounts(self, ingredients, recipe):
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                ingredient=Ingredients.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Reciep.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(
            recipe=instance,
            ingredients=ingredients
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeGetSerializer(instance, context=context).data


class RecipeFavoriteSerializer(ModelSerializer):
    """ Сериализатор для Favorite и ShoppingCart. """

    class Meta:
        model = Reciep
        fields = '__all__'


class FavoriteAndShoppingCartSerializerBase(ModelSerializer):
    """  Сериализатор для модели Favorite. """

    class Meta:
        model = Favourite
        abstract = True
        fields = ('user', 'recipe',)

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                'Рецепт уже добавлен в избранное.'
            )
        return data


class FavoriteSerializer(FavoriteAndShoppingCartSerializerBase):
    """  Сериализатор для модели Favorite.
    Для связи связей избранных рецептов пользователя.
    """

    class Meta(FavoriteAndShoppingCartSerializerBase.Meta):
        pass


class ShoppingCartSerializer(FavoriteAndShoppingCartSerializerBase):
    """ Сериализатор для модели ShoppingCart.
    Для формирования карзины покупок пользователя.
    """

    class Meta(FavoriteAndShoppingCartSerializerBase.Meta):
        model = ShoppingCart


class ListReciepSerializer(ModelSerializer):
    """Получаем список рецептов."""

    class Meta:
        model = Reciep
        fields = ('id', 'title')
