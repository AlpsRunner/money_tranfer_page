from rest_framework import viewsets

from api.serializers import CustomUserSerializer
from usersapp.models import CustomUser


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    filterset_fields = ['inn', ]
