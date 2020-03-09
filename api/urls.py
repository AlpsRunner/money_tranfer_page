from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import CustomUserViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', CustomUserViewSet, base_name='users')

urlpatterns = [
    path('', include(router.urls)),
]
