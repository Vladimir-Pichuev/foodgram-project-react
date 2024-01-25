import base64
from rest_framework.serializers import ModelSerializer, ImageField, HiddenField, CurrentUserDefault
from django.core.files.base import ContentFile

from .models import Ingredients, Tags, Reciep


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredients
        fields = '__all__'


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'


class ReciepSerializerRead(ModelSerializer):

    class Meta:
        model = Reciep
        fields = '__all__'

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class ReciepSerializerWrite(ModelSerializer):
    author = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Reciep
        fields = '__all__'
