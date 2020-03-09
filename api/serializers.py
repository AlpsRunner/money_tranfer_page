from rest_framework import serializers

from usersapp.models import CustomUser


class CustomUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomUser
        fields = 'inn', 'balance'
