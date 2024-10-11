from django.utils.text import slugify
from django.utils import timezone


def generate_sku(name, category):
    """
    Generates a SKU based on the product name and category.

    The SKU is composed of:
    - The first 3 characters of the product's name (slugified),
    - The first 4 characters of the category name in uppercase,
    - The current date (in YYYY-MM-DD format) to ensure uniqueness.
    """
    base_sku = slugify(name[:3])
    category_initial = category.name[:4].upper()
    current_date = timezone.now().strftime('%Y-%m-%d')

    return f"{category_initial}-{base_sku}-{current_date}"
