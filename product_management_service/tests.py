from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import Product, Category
from django.contrib.auth.models import User

# Create your tests here.


class ProductManagementTests(TestCase):
    def setUp(self):
        # Set up API client
        self.client = APIClient()

        # Create an admin user for testing permissions
        self.admin_user = User.objects.create_superuser(
            username="admin", password="adminpass", email="admin@example.com"
        )

        # Create a regular user
        self.regular_user = User.objects.create_user(
            username="user", password="userpass", email="user@example.com"
        )

        # Authenticate admin user for product/category management
        self.client.login(username="admin", password="adminpass")

        # Create a category
        self.category = Category.objects.create(name="Electronics")

        # URL endpoints
        self.product_url = reverse('product-list')
        self.category_url = reverse('category-list')

        # Create a product
        self.product = Product.objects.create(
            name="Laptop",
            sku="LAP12345",
            price=999.99,
            stock_quantity=10,
            category=self.category
        )

    def tearDown(self):
        self.client.logout()

    # Test successful product creation
    def test_create_product(self):
        data = {
            "name": "Smartphone",
            "sku": "SM12345",
            "price": 499.99,
            "stock_quantity": 5,
            "category": self.category.id
        }
        response = self.client.post(self.product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Test failure when creating product with negative price
    def test_create_product_with_negative_price(self):
        data = {
            "name": "Smartphone",
            "sku": "SM12345",
            "price": -100,
            "stock_quantity": 5,
            "category": self.category.id
        }
        response = self.client.post(self.product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test failure when creating product with negative stock quantity
    def test_create_product_with_negative_stock(self):
        data = {
            "name": "Smartphone",
            "sku": "SM12345",
            "price": 499.99,
            "stock_quantity": -5,
            "category": self.category.id
        }
        response = self.client.post(self.product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test fetching the list of products
    def test_get_product_list(self):
        response = self.client.get(self.product_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    # Test searching by product name
    def test_search_product(self):
        response = self.client.get(self.product_url + '?search=Laptop')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    # Test filtering by price
    def test_filter_product_by_price(self):
        response = self.client.get(self.product_url + '?price=999.99')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    # Test updating product details
    def test_update_product(self):
        data = {
            "name": "Updated Laptop",
            "sku": "LAP12345",
            "price": 1099.99,
            "stock_quantity": 15,
            "category": self.category.id
        }
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Laptop')

    # Test deleting product
    def test_delete_product(self):
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    # Test creating a new category
    def test_create_category(self):
        data = {"name": "Books"}
        response = self.client.post(self.category_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Test fetching the list of categories
    def test_get_category_list(self):
        response = self.client.get(self.category_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    # Test that regular users cannot manage products
    def test_regular_user_cannot_manage_products(self):
        self.client.logout()
        self.client.login(username="user", password="userpass")

        data = {
            "name": "Tablet",
            "sku": "TAB12345",
            "price": 299.99,
            "stock_quantity": 20,
            "category": self.category.id
        }
        response = self.client.post(self.product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Test failure when creating product with an empty name
    def test_create_product_with_empty_name(self):
        data = {
            "name": "",
            "sku": "SM12345",
            "price": 499.99,
            "stock_quantity": 5,
            "category": self.category.id
        }
        response = self.client.post(self.product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test updating a product with invalid data (negative price)
    def test_update_product_with_invalid_data(self):
        data = {
            "name": "Invalid Laptop",
            "sku": "LAP54321",
            "price": -999.99,  # Negative price should be invalid
            "stock_quantity": 10,
            "category": self.category.id
        }
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
