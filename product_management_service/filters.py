from django_filters import rest_framework as filters
from .models import Product

class ProductFilter(filters.FilterSet):
    """
    A FilterSet class that provides filtering options for the Product model.

    This class allows users to filter products based on:
    - **Name**: Performs a case-insensitive search for product names.
    - **Category**: Filters products by category name (case-insensitive).
    - **Price Range**: Filters products with price greater than or equal to a minimum 
      value and/or less than or equal to a maximum value.

    Attributes:
    -----------
    name : CharFilter
        Filters products whose names contain the specified value (case-insensitive).
    category : CharFilter
        Filters products that belong to a specific category, based on the category name.
    min_price : NumberFilter
        Filters products with a price greater than or equal to the specified minimum price.
    max_price : NumberFilter
        Filters products with a price less than or equal to the specified maximum price.

    Example Usage:
    --------------
    - `?name=shirt` : Returns all products with "shirt" in their name.
    - `?category=electronics` : Returns all products under the "electronics" category.
    - `?min_price=50&max_price=300` : Returns all products priced between 50 and 300 inclusive.

    Meta:
    -----
    model : Product
        The model class to apply the filters on.
    fields : list
        A list of field names allowed for filtering.

    """

    # Filters by product name (case-insensitive search)
    name = filters.CharFilter(lookup_expr='icontains')  
    
    # Filters by the name of the category (case-insensitive search)
    category = filters.CharFilter(field_name='category__name', lookup_expr='icontains')  
    
    # Filters products with a price greater than or equal to the specified minimum price
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')  
    
    # Filters products with a price less than or equal to the specified maximum price
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')  

    class Meta:
        """
        Meta options for the ProductFilter.

        Attributes:
        -----------
        model : Product
            Specifies that this filter applies to the Product model.
        fields : list
            Defines the fields available for filtering: name, category, min_price, max_price.
        """
        model = Product
        fields = ['name', 'category', 'min_price', 'max_price']
