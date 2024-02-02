from django.contrib import admin

from .models import MyUsers, Follow


class MyUsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email')
    list_display_links = ('id', 'username')
    search_fields = ('username',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'following')
    list_display_links = ('id', 'user')
    search_fields = ('user',)


admin.site.register(MyUsers, MyUsersAdmin)
admin.site.register(Follow, FollowAdmin)
