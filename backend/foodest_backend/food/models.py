from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

"""TAG_CHOICE = [
    (1, 'Завтрак'),
    (2, 'Обед'),
    (3, 'Ужин'),
]"""

"""
UNITS_CHOICE = [
    ('Шт.', 'Штук'),
    ('Гр.', 'Грамм'),
    ('ст.ложку', 'ст.ложку'),
    ('чайная ложка', 'чайная ложка'),
]
"""

User = get_user_model()


class Ingredients(models.Model):
    """Модель ингридиента."""
    ingredients_name = models.CharField(
        max_length=100, verbose_name='Название ингридиента')
    quantity = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, 'Не может быть меньше 1 ингредиента.'),
            MaxValueValidator(30, 'Слишком много ингридиентов.')
        ],
        verbose_name='Количество'
    )
    measurement_unit = models.CharField(
        max_length=20, verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ['ingredients_name']

    def __str__(self):
        return self.ingredients_name


class Tags(models.Model):
    """Модель тегов."""
    title = models.CharField(max_length=100, unique=True, verbose_name='Тег')
    color_code = models.CharField(
        max_length=7, unique=True, verbose_name='Цветовой НЕХ-код'
    )
    slug = models.SlugField(max_length=10, unique=True, verbose_name='Слаг')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Reciep(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User,
        related_name='recieps',
        on_delete=models.SET_NULL,
        verbose_name='Автор',
        null=True
    )
    title = models.CharField('Заголовок', max_length=200)
    image = models.ImageField(
        verbose_name='Изображение', upload_to='reciep_photo/%Y/%m/%d/',
        null=True
    )
    content = models.TextField('Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredients,
        help_text='Начните вводить ингридиент',
        verbose_name='Ингридиент',
        related_name='recieps',
        through='IngredientInRecipe',
    )
    tag = models.ManyToManyField(
        Tags,
        verbose_name='Тег',
        related_name='recieps'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MaxValueValidator(
                300,
                message='Имеет ли смысл так долго готовить?'
            ),
            MinValueValidator(
                1,
                message='Вы хотите добавить салат змейка?:)'
            )
        ],
        verbose_name='Время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True
    )
    update_reciep = models.DateField(
        verbose_name='Дата обновления рецепта', auto_now=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title


class ShopingList(models.Model):
    """Модель корзины."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Reciep,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Покупки'

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Корзину покупок'


class Favourite(models.Model):
    """ Модель Избранное """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Reciep,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class IngredientInRecipe(models.Model):
    """ Модель для связи Ингридиента и Рецепта """

    recipe = models.ForeignKey(
        Reciep,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(1, message='Минимальное количество 1!')]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return (
            f'{self.ingredient.name} ({self.ingredient.measurement_unit}) - {self.amount} '
        )