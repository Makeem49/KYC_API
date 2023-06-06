from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from rest_framework.authtoken.views import obtain_auth_token
from .views import UserListView, UserCreateView

urlpatterns = [
    path('', UserListView.as_view(), name='user_list_create_view'),
    path('signup/', UserCreateView.as_view(), name='create_view'),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name ='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name ='token_refresh'),
]

