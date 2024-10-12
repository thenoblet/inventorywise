from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Product, Category
from api.serializers import ProductSerializer, CategorySerializer
from .permissions import IsAdminOrReadOnly


class ProductPagination(PageNumberPagination):
    """
    Custom pagination class for product listings.

    Attributes:
        page_size (int): Default number of items per page.
        page_size_query_param (str): Parameter name to allow clients to
        set the page size.
        max_page_size (int): Maximum number of items per page.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductList(APIView):
    """
    Handles GET and POST requests for Product objects.

    GET: Returns a paginated list of all products, allowing for filtering
    and searching.
    POST: Creates a new product instance.

    Permission:
        Only admin users can create a product, but everyone can view the
        product list.
    """
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        """
        Retrieves a list of products, applying filters, search, and pagination.

        Args:
            request: The HTTP request object.

        Returns:
            Response: A paginated list of serialized product data.
        """
        queryset = Product.objects.all()

        # Apply filters and search
        filter_backends = [DjangoFilterBackend, filters.SearchFilter]
        for backend in filter_backends:
            queryset = backend().filter_queryset(request, queryset, self)

        # Apply pagination
        paginator = ProductPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Creates a new product based on the provided data.

        Args:
            request: The HTTP request object.

        Returns:
            Response: Serialized product data with status 201 if successful,
            or validation errors with status 400.
        """
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetail(APIView):
    """
    Handles GET, PUT, and DELETE requests for a single Product object.

    GET: Returns the details of a single product.
    PUT: Updates an existing product.
    DELETE: Deletes a product.

    Permission:
        Only admin users can update or delete products.
    """
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):
        """
        Retrieves details of a specific product.

        Args:
            request: The HTTP request object.
            pk (int): The primary key of the product.

        Returns:
            Response: Serialized product data.
        """
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Updates a specific product with new data.

        Args:
            request: The HTTP request object.
            pk (int): The primary key of the product.

        Returns:
            Response: Serialized updated product data, or validation errors
            with status 400.
        """
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Deletes a specific product.

        Args:
            request: The HTTP request object.
            pk (int): The primary key of the product.

        Returns:
            Response: Empty response with status 204 on successful deletion.
        """
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryList(APIView):
    """
    Handles GET and POST requests for Category objects.

    GET: Returns a paginated list of all categories, allowing for filtering
    and searching.
    POST: Creates a new category instance.

    Permission:
        Only admin users can create a category, but everyone can view the
        category list.
    """
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        """
        Retrieves a list of categories, applying filters, search,
        and pagination.

        Args:
            request: The HTTP request object.

        Returns:
            Response: A paginated list of serialized category data.
        """
        queryset = Category.objects.all()

        # Apply filters and search
        filter_backends = [DjangoFilterBackend, filters.SearchFilter]
        for backend in filter_backends:
            queryset = backend().filter_queryset(request, queryset, self)

        # Apply pagination
        paginator = ProductPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = CategorySerializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Creates a new category based on the provided data.

        Args:
            request: The HTTP request object.

        Returns:
            Response: Serialized category data with status 201 if successful,
            or validation errors with status 400.
        """
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetail(APIView):
    """
    Handles GET, PUT, and DELETE requests for a single Category object.

    GET: Returns the details of a single category.
    PUT: Updates an existing category.
    DELETE: Deletes a category.

    Permission:
        Only admin users can update or delete categories.
    """
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):
        """
        Retrieves details of a specific category.

        Args:
            request: The HTTP request object.
            pk (int): The primary key of the category.

        Returns:
            Response: Serialized category data.
        """
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Updates a specific category with new data.

        Args:
            request: The HTTP request object.
            pk (int): The primary key of the category.

        Returns:
            Response: Serialized updated category data, or validation errors
            with status 400.
        """
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Deletes a specific category.

        Args:
            request: The HTTP request object.
            pk (int): The primary key of the category.

        Returns:
            Response: Empty response with status 204 on successful deletion.
        """
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
