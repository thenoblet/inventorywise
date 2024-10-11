from django.urls import path
from .views import UserRegisterView, UserProfileView, UserLoginView, UserLogoutView


urlpatterns = [
    path('register', UserRegisterView.as_view(), name="user_register"),
    path('login', UserLoginView.as_view(), name='user_login'),
    path('profile', UserProfileView.as_view(), name='user_profile'),
    path('logout', UserLogoutView.as_view(), name="user_logout")
]