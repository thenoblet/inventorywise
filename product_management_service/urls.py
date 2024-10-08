from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet


# Create a router and register our viewsets with it
router = DefaultRouter()

# Register the ProductViewSet with the router
router.register(r'products', ProductViewSet)

# Register the CategoryViewSet with the router
router.register(r'categories', CategoryViewSet)


# Include the router's URLs in the urlpatterns
urlpatterns = [
    path('', include(router.urls)),
]
