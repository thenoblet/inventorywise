from rest_framework import serializers
from user_management.models import User, Role, Profile, Permission, UserRole, RolePermission
from product_management_service.models import Product, Category, Inventory


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'firstname', 'middlename', 'lastname', 'is_active', 'is_staff']
        extra_kwargs = {
            'password': {'write_only': True}  # Ensure the password is not read back
        }


    def create(self, validated_data):
        """
        Use CustomUserManager to create a user.
        """
        return User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            firstname=validated_data['firstname'],
            middlename=validated_data.get('middlename', ''),
            lastname=validated_data['lastname'],
            is_active=validated_data.get('is_active', True),
            is_staff=validated_data.get('is_staff', False)
        )

    def update(self, instance, validated_data):
        """
        Use CustomUserManager to update a user.
        """
        instance.username = validated_data.get('username', instance.username)
        instance.firstname = validated_data.get('firstname', instance.firstname)
        instance.middlename = validated_data.get('middlename', instance.middlename)
        instance.lastname = validated_data.get('lastname', instance.lastname)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)

        password = validated_data.get('password')
        if password:
            instance.set_password(password)  # Hash the new password if provided

        instance.save()
        return instance
    
    def deactivate_user(self, email):
        """
        Deactivate a user by setting their 'is_active' field to False.
        """
        try:
            # Call the remove_user method from the User model
            self.Meta.model.remove_user(email)
            return {"message": "User has been deactivated."}
        except ValueError as e:
            raise serializers.ValidationError(str(e))


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'



# Product management serialisers

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


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'