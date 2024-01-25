from django.contrib import admin

from .models import (
    Reciep, Ingredients, Tags, ShopingList
)


class ReciepAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'title', 'image', 'content')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'content')


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredients_name', 'quantity', 'measurement_unit')
    list_display_links = ('id', 'ingredients_name')
    search_fields = ('id', 'ingredients_name')


class TagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug')
    list_display_links = ('id', 'title')
    search_fields = ('id', 'title')


class ShopingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_display_links = ('recipe',)
    search_fields = ('recipe',)


admin.site.register(Reciep, ReciepAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(ShopingList, ShopingListAdmin)