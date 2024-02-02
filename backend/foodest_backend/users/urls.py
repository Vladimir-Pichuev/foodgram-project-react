from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

'''
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
'''

from .views import UserViewSet

router = DefaultRouter()

app_name = 'users'

router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path(r'api/auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
