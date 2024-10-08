from rest_framework import serializers
from .models import Product, Category


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.

    This serializer handles the serialization and deserialization of
    Product instances, including validation for price and stock quantity.

    Attributes:
        Meta (class): Contains metadata about the serializer, including
                      the model it is associated with and the fields to
                      be included in serialization.
    """

    class Meta:
        model = Product
        fields = '__all__'

    def validate_price(self, value):
        """
        Validate the price field.

        Args:
            value (Decimal): The value of the price to validate.

        Raises:
            ValidationError: If the price is negative.

        Returns:
            Decimal: The validated price value.
        """
        if value < 0:
            raise serializers.ValidationError("Price must be a positive\
                                              number.")
        return value

    def validate_stock_quantity(self, value):
        """
        Validate the stock_quantity field.

        Args:
            value (int): The value of the stock quantity to validate.

        Raises:
            ValidationError: If the stock quantity is negative.

        Returns:
            int: The validated stock quantity value.
        """
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be\
                                              negative.")
        return value


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.

    This serializer handles the serialization and deserialization of
    Category instances.

    Attributes:
        Meta (class): Contains metadata about the serializer, including
                      the model it is associated with and the fields to
                      be included in serialization.
    """

    class Meta:
        model = Category
        fields = '__all__'
