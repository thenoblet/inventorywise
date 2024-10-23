from django.contrib import admin
from django.urls import path, include
from .views import ApiStatusView, ApiRootView


urlpatterns = [
    path('status', ApiStatusView.as_view(), name='api_status'),
    path('', ApiRootView.as_view(), name='root_view')
]