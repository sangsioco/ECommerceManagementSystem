# E-Commerce Management System
Author: Sara Angsioco 
Date: 6/29/2024

Instruction:
1. Download the app.py to your desktop or use git clone
2. Create and activate a virtual environment:

The application will be available at http://127.0.0.1:5000.

API Endpoints \
Customer Management\
GET /customers: Retrieve a list of all customers.\
POST /customers: Add a new customer.\
PUT /customers/int:id: Update an existing customer.\
DELETE /customers/int:id: Delete a customer.\
Customer Account Management\\
POST /customer_accounts: Create a new customer account.
GET /customer_accounts/int:id: Retrieve a customer account.
PUT /customer_accounts/int:id: Update a customer account.
DELETE /customer_accounts/int:id: Delete a customer account.
Product Management
POST /products: Add a new product.
GET /products: Retrieve a list of all products.
PUT /products/int:id: Update an existing product.
DELETE /products/int:id: Delete a product.
Order Management
POST /orders: Place a new order.
GET /orders/int:id: Retrieve an order.
GET /orders/int:id/track: Track an order.
PUT /orders/int:id: Update an order.
PUT /orders/int:id/cancel: Cancel an order.
GET /customers/int:customer_id/orders: Retrieve orders for a specific customer.
Postman Collections
Develop Postman collections that categorize and group API requests according to their functionality. Create separate collections for Customer Management, Product Management, Order Management

Customer Management: Add requests for adding, updating, retrieving, and deleting customers.
Customer Account Management:Add requests for creating, updating, retrieving, and deleting customer accounts.
Product Management:Add requests for adding, updating, retrieving, and deleting products.
Order Management:Add requests for placing, updating, retrieving, tracking, and canceling orders, as well as retrieving customer-specific orders.
