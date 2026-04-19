# Semantic layer — business descriptions for each table
# This is what makes our Text-to-SQL better than naive implementations

SEMANTIC_LAYER = {
    "customers": {
        "description": "Contains all registered customers on the Indian e-commerce platform. Use this table for customer demographics, location analysis, and tier-based segmentation.",
        "columns": {
            "customer_id": "Unique identifier for each customer",
            "name": "Full name of the customer",
            "email": "Email address of the customer",
            "city": "Indian city where customer is located",
            "state": "Indian state where customer is located",
            "tier": "Customer loyalty tier: bronze (new), silver (regular), gold (frequent), platinum (VIP)",
            "registered_at": "Date and time when customer registered"
        },
        "usage_notes": "Join with orders on customer_id for purchase analysis. Use tier for segmentation. State and city for geographic analysis."
    },
    "products": {
        "description": "Product catalog with pricing and inventory. Use for product performance, category analysis, and brand comparisons.",
        "columns": {
            "product_id": "Unique identifier for each product",
            "name": "Full product name including brand",
            "category": "Product category: Electronics, Fashion, Home & Kitchen, Books, Sports, Beauty, Toys, Automotive, Grocery, Jewellery",
            "brand": "Brand name of the product",
            "price_inr": "Product price in Indian Rupees (INR). Use this for pricing analysis.",
            "stock": "Current inventory stock count"
        },
        "usage_notes": "Join with orders on product_id for sales analysis. Use price_inr for revenue calculations. Category for segment analysis."
    },
    "sellers": {
        "description": "Seller/merchant information. Use for seller performance, geographic distribution, and rating analysis.",
        "columns": {
            "seller_id": "Unique identifier for each seller",
            "name": "Seller business name",
            "city": "City where seller operates",
            "state": "State where seller operates",
            "rating": "Seller rating from 2.5 to 5.0 — higher is better",
            "joined_at": "Date when seller joined the platform"
        },
        "usage_notes": "Join with orders on seller_id. Use rating for quality analysis. State/city for geographic seller distribution."
    },
    "orders": {
        "description": "Central fact table — all purchase transactions. This is the most important table. Use for revenue, order volume, and status analysis.",
        "columns": {
            "order_id": "Unique identifier for each order",
            "customer_id": "Foreign key to customers table",
            "product_id": "Foreign key to products table",
            "seller_id": "Foreign key to sellers table",
            "quantity": "Number of units ordered",
            "amount_inr": "Total order value in Indian Rupees — USE THIS for revenue calculations, never use price_inr directly",
            "status": "Order status: delivered (successful), cancelled (customer cancelled), returned (product returned), processing (in progress)",
            "created_at": "Date and time when order was placed"
        },
        "usage_notes": "Filter by status='delivered' for actual revenue. Use amount_inr for GMV. Join with customers for demographic analysis, products for category analysis."
    },
    "deliveries": {
        "description": "Delivery performance data for fulfilled orders. Use for logistics analysis, courier comparison, and delivery time tracking.",
        "columns": {
            "delivery_id": "Unique identifier for each delivery",
            "order_id": "Foreign key to orders table",
            "courier": "Courier company: Delhivery, BlueDart, DTDC, Ekart, XpressBees, Shadowfax",
            "expected_days": "Promised delivery time in days",
            "actual_days": "Actual days taken for delivery",
            "delivered_at": "Date and time of actual delivery"
        },
        "usage_notes": "Use (actual_days - expected_days) for delay calculation. Positive = delayed, negative = early. Group by courier for performance comparison."
    },
    "reviews": {
        "description": "Customer reviews and ratings for delivered orders. Use for satisfaction analysis, NPS, and product quality insights.",
        "columns": {
            "review_id": "Unique identifier for each review",
            "order_id": "Foreign key to orders table",
            "customer_id": "Foreign key to customers table",
            "rating": "Customer rating from 1 to 5 — 5 is best",
            "comment": "Text review comment from customer",
            "created_at": "Date when review was submitted"
        },
        "usage_notes": "Average rating by category/brand for quality analysis. Join with products for product-level insights. Filter rating <= 2 for complaints."
    }
}

def get_table_description(table_name: str) -> str:
    if table_name not in SEMANTIC_LAYER:
        return ""
    table = SEMANTIC_LAYER[table_name]
    desc = f"Table: {table_name}\n"
    desc += f"Description: {table['description']}\n"
    desc += f"Usage: {table['usage_notes']}\n"
    desc += "Columns:\n"
    for col, col_desc in table['columns'].items():
        desc += f"  - {col}: {col_desc}\n"
    return desc

def get_all_descriptions() -> list:
    descriptions = []
    for table_name, info in SEMANTIC_LAYER.items():
        desc = get_table_description(table_name)
        descriptions.append({"table": table_name, "description": desc})
    return descriptions