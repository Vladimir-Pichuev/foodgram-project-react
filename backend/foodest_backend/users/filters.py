from django_filters import rest_framework as filters

from .models import MyUsers, Follow


class MyUsersFilter(filters.FilterSet):
    """Фильтры для Users."""

    class Meta:
        model = MyUsers
        fields = []
