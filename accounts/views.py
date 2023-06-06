from rest_framework import generics
from rest_framework import permissions
from django.contrib.auth import get_user_model

from .serializers import UserSerializer


User = get_user_model()

class UserListView(generics.ListAPIView):
    """View handling creating a new employee"""
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'

class UserCreateView(generics.CreateAPIView):
    """View handling creating a new employee"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'
