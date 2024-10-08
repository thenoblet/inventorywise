from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    """
    Custom pagination class for product listings.

    This class defines the pagination behavior for Product listings
    in the API. It allows clients to specify the page size and limits
    the maximum page size.

    Attributes:
        page_size (int): The default number of items per page.
        page_size_query_param (str): The query parameter that clients
                                      can use to set the page size.
        max_page_size (int): The maximum number of items that can be
                             requested per page.
    """

    # Number of items per page
    page_size = 10

    # Allow clients to set the page size
    page_size_query_param = 'page_size'

    # Limit the maximum page size
    max_page_size = 100


class ProductViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Product instances.

    This viewset provides the standard actions for a ModelViewSet,
    including listing, creating, retrieving, updating, and deleting
    products. It supports custom pagination, filtering, and searching.

    Attributes:
        queryset (QuerySet): The set of Product instances to be used
                             for this viewset.
        serializer_class (Serializer): The serializer class used for
                                       validating and serializing data.
        permission_classes (list): A list of permission classes that
                                   determine access to this viewset.
                                   By default, only admin users can access it.
        pagination_class (Pagination): The pagination class used for
                                       paginating results.
        filter_backends (list): A list of filter backends used for
                                filtering and searching products.
        search_fields (list): A list of fields to be searched when
                              performing a search query.
        filterset_fields (list): A list of fields that can be used for
                                 filtering the queryset.
    """

    # Queryset for all products
    queryset = Product.objects.all()

    # Serializer class for Product
    serializer_class = ProductSerializer

    # restrict access to admin users
    permission_classes = [IsAdminUser]

    # # Use custom pagination
    pagination_class = ProductPagination

    # Enable filtering and searching
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    # Fields to search
    search_fields = ['name', 'sku', 'category__name']

    # Fields to filter by
    filterset_fields = ['price', 'stock_quantity', 'category']


class CategoryViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Category instances.

    This viewset provides the standard actions for a ModelViewSet,
    including listing, creating, retrieving, updating, and deleting
    categories.

    Attributes:
        queryset (QuerySet): The set of Category instances to be used
                             for this viewset.
        serializer_class (Serializer): The serializer class used for
                                       validating and serializing data.
        permission_classes (list): A list of permission classes that
                                   determine access to this viewset.
                                   By default, only admin users can access it.
    """

    # Queryset for all categories
    queryset = Category.objects.all()

    # Serializer class for Category
    serializer_class = CategorySerializer

    # restrict access to admin users
    permission_classes = [IsAdminUser]
