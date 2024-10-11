from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import Product, Category
from django.contrib.auth.models import User
from threading import Thread

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

    # Test failure when creating product with duplicate SKU
    def test_create_product_with_duplicate_sku(self):
        data = {
            "name": "Tablet",
            "sku": "LAP12345",  # Same SKU as the existing product
            "price": 399.99,
            "stock_quantity": 20,
            "category": self.category.id
        }
        response = self.client.post(self.product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test failure when creating product without a category
    def test_create_product_without_category(self):
        data = {
            "name": "Smartwatch",
            "sku": "SW12345",
            "price": 199.99,
            "stock_quantity": 8,
            "category": None  # No category assigned
        }
        response = self.client.post(self.product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test failure when creating product with non-existent category
    def test_create_product_with_invalid_category(self):
        data = {
            "name": "Smartwatch",
            "sku": "SW12345",
            "price": 199.99,
            "stock_quantity": 8,
            "category": 9999  # Non-existent category
        }
        response = self.client.post(self.product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test failure when creating a product without required fields
    def test_create_product_without_required_fields(self):
        data = {
            "sku": "SM12345",
            "price": 499.99,
            "stock_quantity": 5,
            "category": self.category.id
        }
        response = self.client.post(self.product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    # Test failure when creating a product with invalid SKU format
    def test_create_product_with_invalid_sku(self):
        data = {
            "name": "Smartphone",
            "sku": "",  # Empty SKU or invalid format
            "price": 499.99,
            "stock_quantity": 5,
            "category": self.category.id
        }
        response = self.client.post(self.product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('sku', response.data)

    # Test product pagination
    def test_product_pagination(self):
        # Create more products to test pagination
        for i in range(15):
            Product.objects.create(
                name=f"Product {i}",
                sku=f"SKU-{i}",
                price=100 + i,
                stock_quantity=10 + i,
                category=self.category
            )

        response = self.client.get(self.product_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        # Assuming a page size of 10
        self.assertLessEqual(len(response.data['results']), 10)
        self.assertIn('next', response.data)  # Verify next page exists

    # Test filtering products by category
    def test_filter_product_by_category(self):
        response = self.client.get(self.product_url + f'?category={self.category.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    # Test updating product without changing SKU
    def test_update_product_without_changing_sku(self):
        data = {
            "name": "Laptop",
            "sku": self.product.sku,  # Same SKU
            "price": 1099.99,
            "stock_quantity": 8,
            "category": self.category.id
        }
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['sku'], self.product.sku)  # Verify SKU remains the same

    # Test that regular users cannot delete products
    def test_regular_user_cannot_delete_product(self):
        self.client.logout()
        self.client.login(username="user", password="userpass")

        url = reverse('product-detail', kwargs={'pk': self.product.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Test deleting a category
    def test_delete_category(self):
        url = reverse('category-detail', kwargs={'pk': self.category.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())

    def test_simultaneous_product_updates(self):
    # Create a new product to test on
        product = Product.objects.create(
            name="Tablet", sku="TAB12345", price=300, stock_quantity=20, category=self.category
        )
        url = reverse('product-detail', kwargs={'pk': product.id})

    # First update thread
    def update_product_1():
            data = {"name": "Tablet - Updated 1", "sku": product.sku, "price": 400, "stock_quantity": 10, "category": self.category.id}
            self.client.put(url, data, format='json')

    # Second update thread
    def update_product_2():
            data = {"name": "Tablet - Updated 2", "sku": product.sku, "price": 500, "stock_quantity": 5, "category": self.category.id}
            self.client.put(url, data, format='json')

    # Run both updates simultaneously
            thread1 = Thread(target=update_product_1)
            thread2 = Thread(target=update_product_2)
            thread1.start()
            thread2.start()
            thread1.join()
            thread2.join()

    # Fetch the product to check the final state
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn(response.data['name'], ['Tablet - Updated 1', 'Tablet - Updated 2'])

    def test_create_product_with_large_input(self):
        large_name = "A" * 1000  # Exceeds normal length
        large_sku = "B" * 500

        data = {
            "name": large_name,
            "sku": large_sku,
            "price": 499.99,
            "stock_quantity": 5,
            "category": self.category.id
        }
        response = self.client.post(self.product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_with_zero_price(self):
        data = {
            "name": "Free Product",
            "sku": "FP12345",
            "price": 0,
            "stock_quantity": 10,
            "category": self.category.id
        }
        response = self.client.post(self.product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_with_zero_stock(self):
        data = {
            "name": "Out of Stock Product",
            "sku": "OOS12345",
            "price": 100,
            "stock_quantity": 0,
            "category": self.category.id
        }
        response = self.client.post(self.product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_with_max_price(self):
        data = {
            "name": "Luxury Product",
            "sku": "LX12345",
            "price": 9999999999.99,  # Max price boundary
            "stock_quantity": 5,
            "category": self.category.id
        }
        response = self.client.post(self.product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_product_pagination_empty_list(self):
        Product.objects.all().delete()  # Ensure no products exist
        response = self.client.get(self.product_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        self.assertIn('next', response.data)
        self.assertIsNone(response.data['next'])  # No next page if empty

    def test_search_product_case_insensitive(self):
        response = self.client.get(self.product_url + '?search=laptop')  # All lowercase
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_product_case_sensitive(self):
        response = self.client.get(self.product_url + '?search=LapTop')  # Mixed case
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_products_across_multiple_categories(self):
    # Create another category
        new_category = Category.objects.create(name="Furniture")

    # Create product in the new category
        Product.objects.create(
            name="Chair", sku="CHAIR123", price=50, stock_quantity=15, category=new_category
        )

    # Filter by category (Furniture)
        response = self.client.get(self.product_url + f'?category={new_category.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Chair")

    def test_partial_update_product(self):
        url = reverse('product-detail', kwargs={'pk': self.product.id})

        data = {"price": 799.99}  # Only updating price
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['price']), 799.99) # Cast the response to float since a string was returned
        self.assertEqual(response.data['name'], "Laptop")  # Name remains unchanged

    def test_invalid_url_injection(self):
        response = self.client.get(self.product_url + "?search=<script>alert('XSS')</script>")
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # No crash
        self.assertNotIn('<script>', str(response.data))  # Ensure no malicious content is returned