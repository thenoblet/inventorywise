# InventoryWise

**InventoryWise** is a comprehensive inventory management system designed to streamline and optimise the tracking, management, and organisation of inventory in businesses. Whether you are a small retailer, a warehouse manager, or an e-commerce entrepreneur, InventoryWise provides the tools you need to maintain accurate stock levels, reduce losses, and improve overall efficiency.

## Features

- **User Authentication**: Secure user registration and login with role-based access control to ensure that only authorized personnel can manage inventory.
  
- **Real-time Inventory Tracking**: Monitor stock levels in real-time with automatic updates on inventory changes, ensuring you always know what’s in stock.

- **Product Management**: Easily add, edit, or delete products from your inventory, including detailed descriptions, images, and SKU numbers.

- **Low Stock Alerts**: Receive notifications when inventory levels fall below a specified threshold, helping you avoid stockouts.

- **Reporting and Analytics**: Generate insightful reports on inventory performance, sales trends, and stock turnover rates to aid in decision-making.

- **Search and Filtering**: Quickly find products using a robust search feature and apply filters based on categories, quantities, or other criteria.

- **User-Friendly Interface**: An intuitive dashboard that provides a seamless experience for managing your inventory with minimal training.

- **Multi-Location Support**: Manage inventory across multiple locations or warehouses, making it ideal for businesses with diverse operations.

## Technologies Used

- **Backend**: Django (Python) with Django REST Framework for building APIs.
- **Database**: MySQL
- **Authentication**: JWT (JSON Web Tokens) for secure user authentication.

## Installation

To install and run InventoryWise locally, follow these steps:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/inventorywise.git
   cd inventorywise
   ```

2. **Set up the virtual environment**:

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

3. **Install the dependencies**:

   ```bash
   pip install -r requirements.txt
   pip install -r dev-requirements.txt
   ```

4. **Run the migrations**:

   ```bash
   python manage.py migrate
   ```

5. **Start the development server**:

   ```bash
   python manage.py runserver
   ```

## Contributing

Contributions are welcome! If you would like to contribute to InventoryWise, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive messages.
4. Push your branch and create a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
