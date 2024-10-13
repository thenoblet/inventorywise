from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, Inventory


@receiver(post_save, sender=Product)
def create_inventory_entry(sender, instance, created, **kwargs):
    """
    Automatically creates an inventory entry when a new product is added.
    Updates inventory if product is updated.
    """
    if created:
        Inventory.objects.create(product=instance, stock_in=instance.stock_quantity)
    else:
        inventory = Inventory.objects.get(product=instance)
        inventory.stock_in = instance.stock_quantity
        inventory.update_stock()
        inventory.save()


@receiver(post_delete, sender=Product)
def delete_inventory_entry(sender, instance, **kwargs):
    """
    Updates inventory stock when a product is deleted.
    Reduces stock in inventory (assumes stock out if deleted).
    """
    try:
        inventory = Inventory.objects.get(product=instance)
        inventory.stock_out = inventory.stock_in  # Assume full stock is removed on deletion
        inventory.update_stock()
        inventory.save()
    except Inventory.DoesNotExist:
        pass  # In case no inventory exists for the product
