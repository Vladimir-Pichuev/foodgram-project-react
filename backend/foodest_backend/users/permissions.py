from rest_framework import permissions


class IsAuthorOrJustReading(permissions.BasePermission):
    """Разрешает модификацию объекта только его владельцу."""

    def has_object_permission(self, request, view, obj):
        is_authenticated = request.user and request.user.is_authenticated
        return (request.method in permissions.SAFE_METHODS
                # print(f'атрибуты obj - ' + str(dir(obj)))
                or obj.username == request.user
                or (is_authenticated and request.user.is_admin)
                or (is_authenticated and request.user.is_moderator)
                )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Для работы с Genres и Categories."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_authenticated:
            return request.user.is_admin
        return False


class IsSuperUserOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ к запросам только администратору
    или суперпользователю.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
