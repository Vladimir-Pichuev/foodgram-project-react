from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, TagViewSet, ReciepViewSet


app_name = 'api'

router = DefaultRouter()

router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='Tags')
router.register('reciep', ReciepViewSet, basename='Reciep')

app_name = 'food'

urlpatterns = [
    path('', include(router.urls)),
]