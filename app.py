from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate, ValidationError
from password import my_password

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{my_password}@localhost/fitness_center_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

# ---------------------------------------------------------------------ALL CUSTOMER RELATED-----------------------------------------------------------------------------------
class CustomerSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ("name", "email", "phone", "id")

class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))

# Create instances of schemas
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

# Read customers list
@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers)

# Add customer
@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])

    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "New customer added successfully"}), 201

# Update customer
@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.phone = customer_data['phone']
    db.session.commit()
    return jsonify({"message": "Customer details updated successfully"}), 200

# Delete customer
@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted successfully"}), 200

#----------------------------------------------------------------ALL CUSTOMER ACCOUNT RELATED-------------------------------------------------------------------------------------
from werkzeug.security import generate_password_hash #is this taught in module (needed for password hash)

class CustomerAccountSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    customer_id = fields.Int(required=True)
    customer = fields.Nested('CustomerSchema', only=['name', 'email', 'phone'])

    class Meta:
        fields = ("id", "username", "password", "customer_id", "customer")

class CustomerAccount(db.Model):
    __tablename__ = 'customer_accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer = db.relationship('Customer', backref='customer_account', uselist=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

# Create instances of schemas
customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many=True)

# CRUD for Customer Accounts
@app.route('/customer_accounts', methods=['POST'])
def create_customer_account():
    data = request.get_json()
    if not all(key in data for key in ['username', 'password', 'customer_id']):
        abort(400, description="Missing required fields")
    customer = Customer.query.get_or_404(data['customer_id'])
    new_account = CustomerAccount(username=data['username'], customer=customer)
    new_account.set_password(data['password'])
    db.session.add(new_account)
    db.session.commit()
    return jsonify({"id": new_account.id}), 201

@app.route('/customer_accounts/<int:id>', methods=['GET'])
def get_customer_account(id):
    account = CustomerAccount.query.get_or_404(id)
    return customer_account_schema.jsonify(account)

@app.route('/customer_accounts/<int:id>', methods=['PUT'])
def update_customer_account(id):
    account = CustomerAccount.query.get_or_404(id)
    data = request.get_json()
    if 'username' in data:
        account.username = data['username']
    if 'password' in data:
        account.set_password(data['password'])
    db.session.commit()
    return jsonify({"message": "Customer account updated"})

@app.route('/customer_accounts/<int:id>', methods=['DELETE'])
def delete_customer_account(id):
    account = CustomerAccount.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({"message": "Customer account deleted"})

#------------------------------------------------------------------------ALL PRODUCT RELATED----------------------------------------------------------------------------------
# Define the ProductsSchema
class ProductsSchema(ma.Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))
    stock = fields.Integer(required=True, validate=validate.Range(min=0))

    class Meta:
        fields = ("id", "name", "price", "stock")

# Define the Product model
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

# Create instances of ProductsSchema
product_schema = ProductsSchema()
products_schema = ProductsSchema(many=True)  # for handling multiple products

@app.route('/products', methods=['POST'])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_product = Product(name=product_data['name'], price=product_data['price'], stock=product_data['stock'])
    db.session.add(new_product)
    db.session.commit()
    return product_schema.jsonify(new_product), 201

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    product.name = product_data['name']
    product.price = product_data['price']
    product.stock = product_data['stock']
    db.session.commit()
    return jsonify({"message": "Product updated successfully"}), 200

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200
#------------------------------------------------------------------------ALL ORDERS RELATED-------------------------------------------------------------------------------------
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    status = db.Column(db.String(50), nullable=False, default='Pending')
    delivery_date = db.Column(db.DateTime)
    total_price = db.Column(db.Float, nullable=False, default=0)  # Added total_price field
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    customer = db.relationship('Customer', backref='orders')
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product = db.relationship('Product', backref='order_items', lazy=True)

class OrderSchema(ma.Schema):
    class Meta:
        fields = ("id", "order_date", "status", "delivery_date", "customer_id", "total_price")

class OrderItemSchema(ma.Schema):
    class Meta:
        fields = ("id", "quantity", "price", "product_id", "order_id")

# CREATE INSTANCES FOR ORDER SCHEMA
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

#CREATE INSTANCES FOR ORDER_ITEM SCHEMA
order_item_schema = OrderItemSchema()
order_items_schema = OrderItemSchema(many=True)

# CRUD for Orders
@app.route('/orders', methods=['POST'])
def place_order():
    data = request.get_json()
    customer_id = data.get('customer_id')
    items = data.get('items')  # [{'product_id': 1, 'quantity': 2}, ...]

    if not customer_id or not items:
        abort(400, description="Missing customer_id or items")
    
    customer = Customer.query.get_or_404(customer_id)
    order = Order(customer=customer)
    total_price = 0
    
    for item in items:
        product_id = item.get('product_id')
        quantity = item.get('quantity')
        product = Product.query.get_or_404(product_id)
        
        if product.stock < quantity:
            abort(400, description=f"Not enough stock for product ID {product_id}")
        
        order_item = OrderItem(
            product=product,
            quantity=quantity,
            price=product.price,
            order=order
        )
        total_price += product.price * quantity
        product.stock -= quantity
    
    order.total_price = total_price
    db.session.add(order)
    db.session.commit()
    
    return jsonify({"id": order.id}), 201

@app.route('/orders/<int:id>', methods=['GET'])
def retrieve_order(id):
    order = Order.query.get_or_404(id)
    items = [{'product_id': item.product_id, 'quantity': item.quantity, 'price': item.price} for item in order.items]
    return jsonify({
        "id": order.id,
        "order_date": order.order_date,
        "status": order.status,
        "delivery_date": order.delivery_date,
        "total_price": order.total_price,
        "items": items,
        "customer_id": order.customer_id
    })

@app.route('/orders/<int:id>/track', methods=['GET'])
def track_order(id):
    order = Order.query.get_or_404(id)
    return jsonify({
        "id": order.id,
        "order_date": order.order_date,
        "status": order.status,
        "delivery_date": order.delivery_date
    })

@app.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    order = Order.query.get_or_404(id)
    data = request.get_json()
    
    if 'status' in data:
        order.status = data['status']
    if 'delivery_date' in data:
        order.delivery_date = data['delivery_date']
    
    db.session.commit()
    return jsonify({"message": "Order updated"})

@app.route('/orders/<int:id>/cancel', methods=['PUT'])
def cancel_order(id):
    order = Order.query.get_or_404(id)
    if order.status in ['Shipped', 'Delivered']:
        abort(400, description="Cannot cancel shipped or delivered orders")
    
    order.status = 'Cancelled'
    db.session.commit()
    return jsonify({"message": "Order cancelled"})

@app.route('/customers/<int:customer_id>/orders', methods=['GET'])
def get_customer_orders(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    orders = Order.query.filter_by(customer_id=customer_id).all()
    return orders_schema.jsonify(orders)

#----------------------------------------------------- INITIALIZE THE DATABASE AND CREATE DATA-----------------------------------------------------------------------------------
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
