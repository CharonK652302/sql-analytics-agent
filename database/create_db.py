import sqlite3
import random
from datetime import datetime, timedelta

# Indian data
CITIES = [
    ("Mumbai", "Maharashtra"), ("Delhi", "Delhi"), ("Bangalore", "Karnataka"),
    ("Hyderabad", "Telangana"), ("Chennai", "Tamil Nadu"), ("Kolkata", "West Bengal"),
    ("Pune", "Maharashtra"), ("Ahmedabad", "Gujarat"), ("Jaipur", "Rajasthan"),
    ("Surat", "Gujarat"), ("Lucknow", "Uttar Pradesh"), ("Kochi", "Kerala"),
    ("Chandigarh", "Punjab"), ("Bhopal", "Madhya Pradesh"), ("Indore", "Madhya Pradesh"),
    ("Nagpur", "Maharashtra"), ("Visakhapatnam", "Andhra Pradesh"), ("Coimbatore", "Tamil Nadu"),
]

CATEGORIES = [
    "Electronics", "Fashion", "Home & Kitchen", "Books", "Sports",
    "Beauty", "Toys", "Automotive", "Grocery", "Jewellery"
]

BRANDS = {
    "Electronics": ["Samsung", "OnePlus", "Realme", "boAt", "Noise"],
    "Fashion": ["Myntra", "FabIndia", "W", "Biba", "Libas"],
    "Home & Kitchen": ["Prestige", "Pigeon", "Butterfly", "Hawkins", "Bajaj"],
    "Books": ["Penguin", "HarperCollins", "Rupa", "Westland", "Disha"],
    "Sports": ["Nivia", "Cosco", "Vector", "Spartan", "Yonex"],
    "Beauty": ["Lakme", "Nykaa", "Mamaearth", "WOW", "Himalaya"],
    "Toys": ["Funskool", "Hamleys", "Lego", "Hot Wheels", "Barbie"],
    "Automotive": ["Bosch", "Amaron", "Exide", "MRF", "CEAT"],
    "Grocery": ["Amul", "MTR", "Haldiram", "ITC", "Dabur"],
    "Jewellery": ["Tanishq", "Malabar", "PC Jeweller", "Kalyan", "Reliance Jewels"],
}

PRODUCTS = {
    "Electronics": ["Wireless Earbuds", "Smart Watch", "Power Bank", "Bluetooth Speaker", "Phone Case"],
    "Fashion": ["Kurta Set", "Saree", "Jeans", "Ethnic Dress", "Formal Shirt"],
    "Home & Kitchen": ["Pressure Cooker", "Mixer Grinder", "Induction Cooktop", "Water Purifier", "Iron"],
    "Books": ["Engineering Maths", "UPSC Guide", "Fiction Novel", "Self Help", "Cookbook"],
    "Sports": ["Cricket Bat", "Badminton Racket", "Football", "Yoga Mat", "Dumbbells"],
    "Beauty": ["Face Serum", "Sunscreen", "Hair Oil", "Lipstick", "Moisturizer"],
    "Toys": ["Board Game", "Remote Car", "Building Blocks", "Puzzle", "Doll Set"],
    "Automotive": ["Car Charger", "Dash Cam", "Seat Cover", "Car Perfume", "Tyre Inflator"],
    "Grocery": ["Ghee 1kg", "Basmati Rice 5kg", "Dry Fruits Mix", "Spice Kit", "Health Drink"],
    "Jewellery": ["Gold Earrings", "Silver Bracelet", "Diamond Pendant", "Pearl Necklace", "Bangles Set"],
}

COURIERS = ["Delhivery", "BlueDart", "DTDC", "Ekart", "XpressBees", "Shadowfax"]
STATUSES = ["delivered", "delivered", "delivered", "delivered", "cancelled", "returned", "processing"]
TIERS = ["bronze", "silver", "gold", "platinum"]

def random_date(start_days_ago=365, end_days_ago=0):
    days = random.randint(end_days_ago, start_days_ago)
    return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

def create_database():
    conn = sqlite3.connect("database/ecommerce.db")
    c = conn.cursor()

    # Create tables
    c.executescript("""
    DROP TABLE IF EXISTS customers;
    DROP TABLE IF EXISTS products;
    DROP TABLE IF EXISTS sellers;
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS deliveries;
    DROP TABLE IF EXISTS reviews;

    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        city TEXT,
        state TEXT,
        tier TEXT,
        registered_at TEXT
    );

    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        name TEXT,
        category TEXT,
        brand TEXT,
        price_inr REAL,
        stock INTEGER
    );

    CREATE TABLE sellers (
        seller_id INTEGER PRIMARY KEY,
        name TEXT,
        city TEXT,
        state TEXT,
        rating REAL,
        joined_at TEXT
    );

    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product_id INTEGER,
        seller_id INTEGER,
        quantity INTEGER,
        amount_inr REAL,
        status TEXT,
        created_at TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
    );

    CREATE TABLE deliveries (
        delivery_id INTEGER PRIMARY KEY,
        order_id INTEGER,
        courier TEXT,
        expected_days INTEGER,
        actual_days INTEGER,
        delivered_at TEXT,
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    );

    CREATE TABLE reviews (
        review_id INTEGER PRIMARY KEY,
        order_id INTEGER,
        customer_id INTEGER,
        rating INTEGER,
        comment TEXT,
        created_at TEXT,
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    );
    """)

    # Generate customers
    print("Generating customers...")
    for i in range(1, 2001):
        city, state = random.choice(CITIES)
        c.execute("INSERT INTO customers VALUES (?,?,?,?,?,?,?)", (
            i, f"Customer_{i}", f"customer{i}@email.com",
            city, state, random.choice(TIERS), random_date(730)
        ))

    # Generate products
    print("Generating products...")
    for i in range(1, 501):
        cat = random.choice(CATEGORIES)
        brand = random.choice(BRANDS[cat])
        product = random.choice(PRODUCTS[cat])
        price = round(random.uniform(99, 49999), 2)
        c.execute("INSERT INTO products VALUES (?,?,?,?,?,?)", (
            i, f"{brand} {product}", cat, brand, price, random.randint(0, 500)
        ))

    # Generate sellers
    print("Generating sellers...")
    for i in range(1, 201):
        city, state = random.choice(CITIES)
        c.execute("INSERT INTO sellers VALUES (?,?,?,?,?,?)", (
            i, f"Seller_{i}", city, state,
            round(random.uniform(2.5, 5.0), 1), random_date(1000)
        ))

    # Generate orders
    print("Generating orders...")
    for i in range(1, 10001):
        status = random.choice(STATUSES)
        qty = random.randint(1, 5)
        product_id = random.randint(1, 500)
        c.execute("SELECT price_inr FROM products WHERE product_id=?", (product_id,))
        price = c.fetchone()[0]
        c.execute("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?)", (
            i, random.randint(1, 2000), product_id,
            random.randint(1, 200), qty,
            round(price * qty, 2), status, random_date(365)
        ))

    # Generate deliveries
    print("Generating deliveries...")
    c.execute("SELECT order_id, created_at FROM orders WHERE status='delivered'")
    delivered = c.fetchall()
    for delivery_id, (order_id, created_at) in enumerate(delivered, 1):
        expected = random.randint(3, 7)
        actual = random.randint(1, 12)
        c.execute("INSERT INTO deliveries VALUES (?,?,?,?,?,?)", (
            delivery_id, order_id, random.choice(COURIERS),
            expected, actual, random_date(300)
        ))

    # Generate reviews
    print("Generating reviews...")
    c.execute("SELECT order_id, customer_id FROM orders WHERE status='delivered'")
    delivered_orders = c.fetchall()
    sample = random.sample(delivered_orders, min(3000, len(delivered_orders)))
    comments = ["Great product!", "Fast delivery", "Value for money",
                "Good quality", "Satisfied", "Average", "Could be better", "Excellent!"]
    for review_id, (order_id, customer_id) in enumerate(sample, 1):
        c.execute("INSERT INTO reviews VALUES (?,?,?,?,?,?)", (
            review_id, order_id, customer_id,
            random.randint(1, 5), random.choice(comments), random_date(300)
        ))

    conn.commit()
    conn.close()
    print("Database created: database/ecommerce.db")
    print("Tables: customers, products, sellers, orders, deliveries, reviews")
    print("Records: 2000 customers, 500 products, 200 sellers, 10000 orders")

if __name__ == "__main__":
    create_database()