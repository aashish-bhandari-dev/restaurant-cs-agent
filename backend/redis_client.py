import redis
import json
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import os
import config.settings

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self, host: str, port: int, db: int, password: Optional[str] = None):
        """Initialize Redis client."""
        try: 
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True
            )
            self.client.ping()  # Test connection
            logger.debug("Connected to Redis at %s:%s", host, port)
        except redis.RedisError as e:
            logger.error("Failed to connect to Redis: %s", e)
            raise

    # Restaurant Info Methods
    def get_restaurant_info(self) -> Dict[str, Any]:
        """Get restaurant information."""
        try:
            info = self.client.hgetall("restaurant:info")
            if not info:
                raise ValueError("Restaurant info not found in Redis")
            # Reconstruct contact and hours
            return {
                "name": info.get("name"),
                "address": info.get("address"),
                "contact": {
                    "phone": info.get("contact_phone"),
                    "email": info.get("contact_email")
                },
                "hours": {
                    day: info.get(f"hours_{day.lower()}")
                    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                }
            }
        except redis.RedisError as e:
            logger.error("Error retrieving restaurant info: %s", e)
            raise

    # Menu Methods
    def get_menu_categories(self) -> List[str]:
        """Get list of menu categories."""
        try:
            return list(self.client.smembers("menu:categories"))
        except redis.RedisError as e:
            logger.error("Error retrieving menu categories: %s", e)
            raise

    def get_category_items(self, category_name: str) -> List[Dict[str, Any]]:
        """Get items for a specific category."""
        try:
            item_ids = self.client.lrange(f"menu:category:{category_name}:items", 0, -1)
            items = []
            for item_id in item_ids:
                item = self.client.hgetall(f"menu:item:{item_id}")
                if item:
                    items.append({
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "description": item.get("description"),
                        "price": float(item.get("price")),
                        "is_vegetarian": item.get("is_vegetarian") == "true",
                        "is_gluten_free": item.get("is_gluten_free") == "true"
                    })
            return items
        except redis.RedisError as e:
            logger.error("Error retrieving items for category %s: %s", category_name, e)
            raise

    def get_menu(self) -> Dict[str, Any]:
        """Get the entire menu."""
        try:
            categories = self.get_menu_categories()
            menu = {"categories": []}
            for category in categories:
                category_data = self.client.hgetall(f"menu:category:{category}")
                items = self.get_category_items(category)
                menu["categories"].append({
                    "name": category_data.get("name"),
                    "items": items
                })
            return menu
        except redis.RedisError as e:
            logger.error("Error retrieving menu: %s", e)
            raise

    def get_menu_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific menu item by ID."""
        try:
            item = self.client.hgetall(f"menu:item:{item_id}")
            if not item:
                return None
            return {
                "id": item.get("id"),
                "name": item.get("name"),
                "description": item.get("description"),
                "price": float(item.get("price")),
                "is_vegetarian": item.get("is_vegetarian") == "true",
                "is_gluten_free": item.get("is_gluten_free") == "true"
            }
        except redis.RedisError as e:
            logger.error("Error retrieving menu item %s: %s", item_id, e)
            raise

    # Top Selling Items Methods
    def get_top_selling_items(self, number: int = None, position: int = None) -> List[Dict[str, Any]]:
        """Get top-selling items, optionally by number or specific position."""
        try:
            if position is not None:
                # Get item at specific position (0-based index in Redis)
                items = self.client.zrevrange("top_selling_items", position - 1, position - 1, withscores=True)
                if not items:
                    return []
                item_id, score = items[0]
                item = self.client.hgetall(f"top_selling_item:{item_id}")
                return [{
                    "item_id": item.get("item_id"),
                    "name": item.get("name"),
                    "sales_count": int(item.get("sales_count"))
                }]
            # Get top N items
            end = number - 1 if number else -1
            items = self.client.zrevrange("top_selling_items", 0, end, withscores=True)
            result = []
            for item_id, score in items:
                item = self.client.hgetall(f"top_selling_item:{item_id}")
                result.append({
                    "item_id": item.get("item_id"),
                    "name": item.get("name"),
                    "sales_count": int(item.get("sales_count"))
                })
            return result
        except redis.RedisError as e:
            logger.error("Error retrieving top-selling items: %s", e)
            raise

    # Offers Methods
    def get_offers(self) -> List[Dict[str, Any]]:
        """Get all offers."""
        try:
            offer_ids = self.client.lrange("offers", 0, -1)
            offers = []
            for offer_id in offer_ids:
                offer = self.client.hgetall(f"offer:{offer_id}")
                if offer:
                    offers.append({
                        "id": offer.get("id"),
                        "name": offer.get("name"),
                        "description": offer.get("description"),
                        "price": float(offer.get("price")),
                        "valid_until": offer.get("valid_until")
                    })
            return offers
        except redis.RedisError as e:
            logger.error("Error retrieving offers: %s", e)
            raise

    # Orders Methods
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific order by ID."""
        try:
            order = self.client.hgetall(f"order:{order_id}")
            if not order:
                return None
            items = self.client.lrange(f"order:{order_id}:items", 0, -1)
            order_items = [json.loads(item) for item in items]
            return {
                "order_id": order.get("order_id"),
                "customer_name": order.get("customer_name"),
                "table_number": int(order.get("table_number")),
                "items": order_items,
                "total": float(order.get("total")),
                "status": order.get("status"),
                "timestamp": order.get("timestamp")
            }
        except redis.RedisError as e:
            logger.error("Error retrieving order %s: %s", order_id, e)
            raise

    def add_order(self, order: Dict[str, Any]) -> None:
        """Add a new order."""
        try:
            order_id = order["order_id"]
            with self.client.pipeline() as pipe:
                pipe.hmset(f"order:{order_id}", {
                    "order_id": order["order_id"],
                    "customer_name": order["customer_name"],
                    "table_number": order["table_number"],
                    "total": order["total"],
                    "status": order["status"],
                    "timestamp": order["timestamp"]
                })
                for item in order["items"]:
                    pipe.rpush(f"order:{order_id}:items", json.dumps(item))
                pipe.rpush("orders", order_id)
                pipe.execute()
            logger.debug("Order %s added to Redis", order_id)
        except redis.RedisError as e:
            logger.error("Error adding order %s: %s", order_id, e)
            raise

    # Reservations Methods
    def get_reservation(self, reservation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific reservation by ID."""
        try:
            reservation = self.client.hgetall(f"reservation:{reservation_id}")
            if not reservation:
                return None
            return {
                "reservation_id": reservation.get("reservation_id"),
                "customer_name": reservation.get("customer_name"),
                "party_size": int(reservation.get("party_size")),
                "date": reservation.get("date"),
                "time": reservation.get("time"),
                "status": reservation.get("status")
            }
        except redis.RedisError as e:
            logger.error("Error retrieving reservation %s: %s", reservation_id, e)
            raise

    def add_reservation(self, reservation: Dict[str, Any]) -> None:
        """Add a new reservation."""
        try:
            reservation_id = reservation["reservation_id"]
            with self.client.pipeline() as pipe:
                pipe.hmset(f"reservation:{reservation_id}", reservation)
                pipe.rpush("reservations", reservation_id)
                pipe.execute()
            logger.debug("Reservation %s added to Redis", reservation_id)
        except redis.RedisError as e:
            logger.error("Error adding reservation %s: %s", reservation_id, e)
            raise

    def update_reservation(self, reservation_id: str, updates: Dict[str, Any]) -> None:
        """Update a reservation."""
        try:
            if self.client.exists(f"reservation:{reservation_id}"):
                self.client.hmset(f"reservation:{reservation_id}", updates)
                logger.debug("Reservation %s updated in Redis", reservation_id)
            else:
                raise ValueError(f"Reservation {reservation_id} not found")
        except redis.RedisError as e:
            logger.error("Error updating reservation %s: %s", reservation_id, e)
            raise

# Initialize Redis client
redis_client = RedisClient(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 2)),
    password=os.getenv("REDIS_PASSWORD", None)
)