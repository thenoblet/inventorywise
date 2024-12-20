from django.db import models
from django.utils import timezone

# Create your models here.

class Category(models.Model):
    """
    Represents a category of products.

    Attributes:
        name (str): The name of the category.
        parent_category (ForeignKey): A reference to the parent category,
        allowing for nested categories.
        description (str): A brief description of the category.
        created_at (datetime): The timestamp when the category was created.
        updated_at (datetime): The timestamp when the category was last
        updated.
    """

    name = models.CharField(max_length=255, unique=True)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    description = models.TextField(null=False, default='No description provided')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    # Order by name by default
    class Meta:
        ordering = ['name']


class Product(models.Model):
    """
    Represents a product available for sale.

    Attributes:
        sku (str): A unique identifier for the product (Stock Keeping Unit).
        name (str): The name of the product.
        description (str): A brief description of the product.
        price (Decimal): The price of the product (must be non-negative).
        stock_quantity (PositiveIntegerField): The quantity of the product in stock (must be positive).
        category (ForeignKey): A reference to the category the product belongs to.
        barcode (str): An optional barcode for the product.
        min_stock_threshold (PositiveIntegerField): The minimum stock level to trigger a low-stock alert.
        max_stock_threshold (PositiveIntegerField): The maximum stock level to trigger a surplus alert.
        created_at (datetime): The timestamp when the product was created.
        updated_at (datetime): The timestamp when the product was last updated.
    """

    sku = models.CharField(max_length=50, unique=True, blank=True)  # SKU must be unique
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    # Non-negative price
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)  # Positive stock quantity
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )  # ForeignKey to Category
    barcode = models.CharField(max_length=100, blank=True)
    min_stock_threshold = models.PositiveIntegerField(default=10)
    max_stock_threshold = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='positive_price'
            ),  # Price can't be negative
            models.CheckConstraint(
                check=models.Q(stock_quantity__gte=0),
                name='positive_stock_quantity'
            )  # Stock quantity must be positive
        ]
        # Order by name by default
        ordering = ['name']
        
    def __str__(self):
        return f'{self.name} (SKU: {self.sku})'


class ProductVariant(models.Model):
    """
    Represents variations of a product, such as different colors or sizes.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    variant_name = models.CharField(max_length=50)  # e.g., color, size
    variant_value = models.CharField(max_length=50)  # e.g., red, large
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ['product', 'variant_name', 'variant_value']  # Ensures uniqueness within the same product

    def __str__(self):
        return f'{self.product.name} - {self.variant_name}: {self.variant_value}'
    

class Inventory(models.Model):
    """
    Tracks stock movements in and out of inventory for a given product.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory')
    stock_in = models.PositiveIntegerField(default=0)
    stock_out = models.PositiveIntegerField(default=0)
    current_stock = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """
        Override the save method to update current_stock before saving.
        """
        self.current_stock = self.stock_in - self.stock_out
        super().save(*args, **kwargs)
        
    def update_stock(self):
        """
        Automatically updates the current stock based on incoming and outgoing movements.
        """
        self.current_stock = self.stock_in - self.stock_out
        self.save()
        
    def add_stock(self, quantity):
        """
        Add stock to the inventory and log the movement.
        """
        self.stock_in += quantity
        InventoryMovement.objects.create(product=self.product, movement_type='IN', quantity=quantity)
        self.update_stock()
        
    def remove_stock(self, quantity):
        """
        Remove stock from the inventory and log the movement.
        """
        self.stock_out += quantity
        InventoryMovement.objects.create(product=self.product, movement_type='OUT', quantity=quantity)
        self.update_stock()

    def __str__(self):
        return f'Product: {self.product.name} - Stock-In: {self.stock_in} - Stock-Out: {self.stock_out} - Current Stock: {self.current_stock}'


class InventoryMovement(models.Model):
    """
    Records every movement (in or out) of inventory to track stock changes.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=10, choices=[('IN', 'Stock In'), ('OUT', 'Stock Out')])
    quantity = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.name} - {self.movement_type}: {self.quantity} units on {self.timestamp}'

