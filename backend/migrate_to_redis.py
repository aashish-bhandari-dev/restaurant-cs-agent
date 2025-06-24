import json
import os
import logging
from redis_client import redis_client

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_json_data():
    """Load data from restaurant_data.json."""
    try:
        if not os.path.exists("restaurant_data.json"):
            raise FileNotFoundError("restaurant_data.json not found")
        with open("restaurant_data.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Failed to load restaurant_data.json: %s", e)
        raise

def migrate_restaurant_info(data):
    """Migrate restaurant info to Redis if not already present."""
    if not redis_client.client.exists("restaurant:info"):
        restaurant = data["restaurant"]
        with redis_client.client.pipeline() as pipe:
            pipe.hset("restaurant:info", mapping={
                "name": restaurant["name"],
                "address": restaurant["address"],
                "contact_phone": restaurant["contact"]["phone"],
                "contact_email": restaurant["contact"]["email"],
                **{f"hours_{day.lower()}": restaurant["hours"][day] for day in restaurant["hours"]}
            })
            pipe.execute()
        logger.debug("Migrated restaurant info")
    else:
        logger.debug("Restaurant info already exists, skipping migration")

def migrate_menu(data):
    """Migrate menu data to Redis if not already present."""
    if not redis_client.client.exists("menu:categories"):
        with redis_client.client.pipeline() as pipe:
            for category in data["menu"]["categories"]:
                category_name = category["name"]
                pipe.sadd("menu:categories", category_name)
                pipe.hset(f"menu:category:{category_name}", mapping={"name": category_name})
                for item in category["items"]:
                    item_id = item["id"]
                    pipe.rpush(f"menu:category:{category_name}:items", item_id)
                    pipe.hset(f"menu:item:{item_id}", mapping={
                        "id": item["id"],
                        "name": item["name"],
                        "description": item["description"],
                        "price": item["price"],
                        "is_vegetarian": str(item["is_vegetarian"]).lower(),
                        "is_gluten_free": str(item["is_gluten_free"]).lower()
                    })
            pipe.execute()
        logger.debug("Migrated menu data")
    else:
        logger.debug("Menu categories already exist, skipping migration")

def migrate_top_selling_items(data):
    """Migrate top-selling items to Redis if not already present."""
    if not redis_client.client.exists("top_selling_items"):
        with redis_client.client.pipeline() as pipe:
            for item in data["top_selling_items"]:
                item_id = item["item_id"]
                pipe.zadd("top_selling_items", {item_id: item["sales_count"]})
                pipe.hset(f"top_selling_item:{item_id}", mapping={
                    "item_id": item["item_id"],
                    "name": item["name"],
                    "sales_count": item["sales_count"]
                })
            pipe.execute()
        logger.debug("Migrated top-selling items")
    else:
        logger.debug("Top-selling items already exist, skipping migration")

def migrate_offers(data):
    """Migrate offers to Redis if not already present."""
    if not redis_client.client.exists("offers"):
        with redis_client.client.pipeline() as pipe:
            for offer in data["offers"]:
                offer_id = offer["id"]
                pipe.rpush("offers", offer_id)
                pipe.hset(f"offer:{offer_id}", mapping={
                    "id": offer["id"],
                    "name": offer["name"],
                    "description": offer["description"],
                    "price": offer["price"],
                    "valid_until": offer["valid_until"]
                })
            pipe.execute()
        logger.debug("Migrated offers")
    else:
        logger.debug("Offers already exist, skipping migration")

def migrate_orders(data):
    """Migrate orders to Redis, checking for existing orders."""
    existing_orders = redis_client.client.lrange("orders", 0, -1)
    with redis_client.client.pipeline() as pipe:
        for order in data["orders"]:
            order_id = order["order_id"]
            if order_id not in existing_orders:
                redis_client.add_order(order)
                pipe.rpush("orders", order_id)  
        pipe.execute()
    logger.debug("Migrated orders")

def migrate_reservations(data):
    """Migrate reservations to Redis, checking for existing reservations."""
    existing_reservations = redis_client.client.lrange("reservations", 0, -1)
    with redis_client.client.pipeline() as pipe:
        for reservation in data["reservations"]:
            reservation_id = reservation["reservation_id"]
            if reservation_id not in existing_reservations:
                redis_client.add_reservation(reservation)
                pipe.rpush("reservations", reservation_id) 
        pipe.execute()
    logger.debug("Migrated reservations")

def main():
    """Main migration function."""
    data = load_json_data()
    migrate_restaurant_info(data)
    migrate_menu(data)
    migrate_top_selling_items(data)
    migrate_offers(data)
    migrate_orders(data)
    migrate_reservations(data)
    logger.info("Migration to Redis completed successfully")

if __name__ == "__main__":
    main()