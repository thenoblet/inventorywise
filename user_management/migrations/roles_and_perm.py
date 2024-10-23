from django.db import migrations, transaction, models


def create_roles_and_permissions(apps, schema_editor):
    # Get the models we need to work with
    Role = apps.get_model('user_management', 'Role')
    Permission = apps.get_model('user_management', 'Permission')
    RolePermission = apps.get_model('user_management', 'RolePermission')

    # Define roles to be created
    roles = [
        ('admin', 'Administrator'),
        ('stock_manager', 'Stock Manager'),
        ('sales_rep', 'Sales Representative'),
    ]

    # Define permissions to be created
    permissions = [
        ('create_user', 'can create user'),
        ('update_user', 'can update user'),
        ('delete_user', 'can delete user'),
        ('view_item', 'Can view items'),
        ('edit_item', 'Can edit items'),
        ('delete_item', 'Can delete items'),
    ]

    # Use transaction to ensure atomicity
    with transaction.atomic():
        for role_name, description in roles:
            Role.objects.get_or_create(name=role_name, description=description)

        for permission_name, description in permissions:
            Permission.objects.get_or_create(name=permission_name, description=description)

        role_permissions = {
            'admin': ['create_user', 'update_user', 'delete_user', 'view_item', 'edit_item', 'delete_item'],
            'stock_manager': ['view_item', 'edit_item'],
            'sales_rep': ['view_item'],
        }

        for role_name, perm_names in role_permissions.items():
            try:
                role = Role.objects.get(name=role_name)
            except Role.DoesNotExist:
                raise ValueError(f"Role '{role_name}' does not exist.")

            for perm_name in perm_names:
                try:
                    permission = Permission.objects.get(name=perm_name)
                except Permission.DoesNotExist:
                    raise ValueError(f"Permission '{perm_name}' does not exist.")

                RolePermission.objects.get_or_create(role=role, permission=permission)


class Migration(migrations.Migration):
    dependencies = [
        ('user_management', '0001_initial'),  # Adjust to your initial migration
    ]

    operations = [
        migrations.RunPython(create_roles_and_permissions),
    ]
