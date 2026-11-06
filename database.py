import psycopg2
from psycopg2.extras import DictCursor
from typing import List, Dict, Any, Optional, Tuple
import sys
import os
import configparser


class Database:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            config = configparser.ConfigParser()
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
            config.read(config_path, encoding="utf-8")
            db = config["database"]
            self.connection = psycopg2.connect(
                host=db["host"],
                database=db["name"],
                user=db["user"],
                password=db["password"],
                port=db["port"]
            )
            return True
        except Exception:
            self.connection = None
            return False
        except Exception:
            self.connection = None
            return False

    def close(self):
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        results = []
        try:
            with self.connection.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, params or ())
                if cursor.description:
                    results = [dict(row) for row in cursor.fetchall()]
                self.connection.commit()
        except Exception:
            self.connection.rollback()
        return results

    def execute_update(self, query: str, params: tuple = None) -> int:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()
                return cursor.rowcount
        except Exception:
            self.connection.rollback()
            return 0

    def get_all_products(self) -> List[Dict[str, Any]]:
        query = """
        SELECT sku, name, unit, price, description, supplier, 
               manufacturer, photo_filename, discount, category,
               quantity,
               price - (price * discount / 100) as price_with_discount
        FROM products
        ORDER BY sku
        """
        return self.execute_query(query)

    def get_product_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        query = """
        SELECT sku, name, unit, price, description, supplier, 
               manufacturer, photo_filename, discount, category,
               quantity
        FROM products
        WHERE sku = %s
        """
        result = self.execute_query(query, (sku,))
        return result[0] if result else None

    def add_product(self, product_data: Dict[str, Any]) -> bool:
        query = """
        INSERT INTO products (sku, name, unit, price, description, supplier, 
                            manufacturer, photo_filename, discount, category, quantity)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            price = int(product_data.get('price', 0)) if str(product_data.get('price', '')).isdigit() else 0
            discount = int(product_data.get('discount', 0)) if str(product_data.get('discount', '')).isdigit() else 0
            quantity = int(product_data.get('quantity', 0)) if str(product_data.get('quantity', '')).isdigit() else 0

            params = (
                product_data.get('sku'),
                product_data.get('name'),
                product_data.get('unit'),
                price,
                product_data.get('description'),
                product_data.get('supplier'),
                product_data.get('manufacturer'),
                product_data.get('photo_filename'),
                discount,
                product_data.get('category'),
                quantity
            )
            return self.execute_update(query, params) > 0
        except Exception:
            return False

    def update_product(self, product_data: Dict[str, Any]) -> bool:
        query = """
        UPDATE products 
        SET name = %s, unit = %s, price = %s, description = %s, 
            supplier = %s, manufacturer = %s, photo_filename = %s, 
            discount = %s, category = %s, quantity = %s
        WHERE sku = %s
        """
        try:
            price = int(product_data.get('price', 0)) if str(product_data.get('price', '')).isdigit() else 0
            discount = int(product_data.get('discount', 0)) if str(product_data.get('discount', '')).isdigit() else 0
            quantity = int(product_data.get('quantity', 0)) if str(product_data.get('quantity', '')).isdigit() else 0

            params = (
                product_data.get('name'),
                product_data.get('unit'),
                price,
                product_data.get('description'),
                product_data.get('supplier'),
                product_data.get('manufacturer'),
                product_data.get('photo_filename'),
                discount,
                product_data.get('category'),
                quantity,
                product_data.get('sku')
            )
            return self.execute_update(query, params) > 0
        except Exception:
            return False

    def delete_product(self, sku: str) -> bool:
        check_query = "SELECT COUNT(*) FROM order_items WHERE product_id = %s"
        result = self.execute_query(check_query, (sku,))

        if result and result[0]['count'] > 0:
            return False

        query = "DELETE FROM products WHERE sku = %s"
        return self.execute_update(query, (sku,)) > 0

    def update_product_quantity(self, sku: str, quantity_change: int) -> bool:
        query = """
        UPDATE products 
        SET quantity = quantity + %s
        WHERE sku = %s AND quantity + %s >= 0
        """
        return self.execute_update(query, (quantity_change, sku, quantity_change)) > 0

    def get_all_orders(self) -> List[Dict[str, Any]]:
        query = """
        SELECT 
            o.order_id as id,
            o.order_date,
            o.delivery_date,
            w.address as delivery_point,
            o.pickup_code,
            o.status,
            u.full_name as customer_name,
            u.user_id as customer_id,
            w.warehouse_id,
            (SELECT SUM(oi.quantity) FROM order_items oi WHERE oi.order_id = o.order_id) as total_items
        FROM orders o
        LEFT JOIN warehouses w ON o.warehouse_id = w.warehouse_id
        LEFT JOIN users u ON o.customer_id = u.user_id
        ORDER BY o.order_date DESC
        """

        orders = self.execute_query(query)

        for order in orders:
            order_id = order['id']
            order['sku_string'] = self.get_order_sku_string(order_id)

        return orders

    def get_order_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        query = """
        SELECT 
            o.order_id as id,
            o.order_date,
            o.delivery_date,
            w.address as delivery_point,
            o.pickup_code,
            o.status,
            u.full_name as customer_name,
            u.user_id as customer_id,
            w.warehouse_id,
            (SELECT SUM(oi.quantity) FROM order_items oi WHERE oi.order_id = o.order_id) as total_items
        FROM orders o
        LEFT JOIN warehouses w ON o.warehouse_id = w.warehouse_id
        LEFT JOIN users u ON o.customer_id = u.user_id
        WHERE o.order_id = %s
        """
        result = self.execute_query(query, (order_id,))
        return result[0] if result else None

    def get_order_with_items(self, order_id: int) -> Optional[Dict[str, Any]]:
        order_query = """
        SELECT 
            o.order_id as id,
            o.order_date,
            o.delivery_date,
            w.address as delivery_point,
            o.pickup_code,
            o.status,
            u.full_name as customer_name,
            u.user_id as customer_id,
            w.warehouse_id
        FROM orders o
        LEFT JOIN warehouses w ON o.warehouse_id = w.warehouse_id
        LEFT JOIN users u ON o.customer_id = u.user_id
        WHERE o.order_id = %s
        """

        items_query = """
        SELECT 
            oi.product_id as sku, 
            oi.quantity, 
            p.name, 
            p.price, 
            p.discount,
            (p.price * oi.quantity) as total
        FROM order_items oi
        LEFT JOIN products p ON oi.product_id = p.sku
        WHERE oi.order_id = %s
        """

        order = self.execute_query(order_query, (order_id,))
        if not order:
            return None

        items = self.execute_query(items_query, (order_id,))

        result = order[0]
        result['items'] = items
        result['total_amount'] = sum(item['total'] for item in items)

        return result

    def add_order(self, order_data: Dict[str, Any]) -> int:
        try:
            customer_query = "SELECT user_id FROM users WHERE role_id = 2 LIMIT 1"
            customer_result = self.execute_query(customer_query)
            customer_id = customer_result[0]['user_id'] if customer_result else 7

            delivery_point = order_data.get('delivery_point', '')
            warehouse_id = 1

            if delivery_point:
                warehouse_query = "SELECT warehouse_id FROM warehouses WHERE address = %s LIMIT 1"
                warehouse_result = self.execute_query(warehouse_query, (delivery_point,))
                if warehouse_result:
                    warehouse_id = warehouse_result[0]['warehouse_id']

            pickup_code = order_data.get('pickup_code', '')
            if not pickup_code:
                import random
                pickup_code = str(random.randint(100000, 999999))

            query = """
            INSERT INTO orders (order_date, delivery_date, warehouse_id, 
                              customer_id, pickup_code, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING order_id
            """

            with self.connection.cursor() as cursor:
                cursor.execute(query, (
                    order_data.get('order_date'),
                    order_data.get('delivery_date'),
                    warehouse_id,
                    customer_id,
                    pickup_code,
                    order_data.get('status', 'Новый')
                ))
                order_id = cursor.fetchone()[0]
                self.connection.commit()
                return order_id

        except Exception:
            self.connection.rollback()
            return 0

    def update_order(self, order_data: Dict[str, Any]) -> bool:
        try:
            customer_id = order_data.get('customer_id')

            if not customer_id:
                customer_query = "SELECT user_id FROM users WHERE role_id = 2 LIMIT 1"
                customer_result = self.execute_query(customer_query)
                customer_id = customer_result[0]['user_id'] if customer_result else 7

            delivery_point = order_data.get('delivery_point', '')
            warehouse_id = None

            if delivery_point:
                warehouse_query = "SELECT warehouse_id FROM warehouses WHERE address ILIKE %s LIMIT 1"
                warehouse_result = self.execute_query(warehouse_query, (f"%{delivery_point}%",))

                if not warehouse_result:
                    warehouse_query = "SELECT warehouse_id FROM warehouses LIMIT 1"
                    warehouse_result = self.execute_query(warehouse_query)

                if warehouse_result:
                    warehouse_id = warehouse_result[0]['warehouse_id']

            if not warehouse_id:
                warehouse_query = "SELECT warehouse_id FROM warehouses LIMIT 1"
                warehouse_result = self.execute_query(warehouse_query)
                if warehouse_result:
                    warehouse_id = warehouse_result[0]['warehouse_id']
                else:
                    warehouse_id = 1

            query = """
            UPDATE orders 
            SET order_date = %s, delivery_date = %s, warehouse_id = %s,
                customer_id = %s, pickup_code = %s, status = %s
            WHERE order_id = %s
            """

            params = (
                order_data.get('order_date'),
                order_data.get('delivery_date'),
                warehouse_id,
                customer_id,
                order_data.get('pickup_code'),
                order_data.get('status'),
                order_data.get('id')
            )

            return self.execute_update(query, params) > 0
        except Exception:
            return False

    def get_order_sku_string(self, order_id: int) -> str:
        try:
            items = self.get_order_items(order_id)
            if not items:
                return ""

            sku_parts = []
            for item in items:
                sku = str(item.get('sku', ''))
                quantity = str(item.get('quantity', 0))
                if sku:
                    sku_parts.append(sku)
                    sku_parts.append(quantity)

            return ", ".join(sku_parts)
        except Exception:
            return ""

    def delete_order(self, order_id: int) -> bool:
        try:
            delete_items_query = "DELETE FROM order_items WHERE order_id = %s"
            self.execute_update(delete_items_query, (order_id,))

            delete_order_query = "DELETE FROM orders WHERE order_id = %s"
            return self.execute_update(delete_order_query, (order_id,)) > 0
        except Exception:
            return False

    def add_order_item(self, order_id: int, product_sku: str, quantity: int) -> bool:
        try:
            price_query = "SELECT price FROM products WHERE sku = %s"
            price_result = self.execute_query(price_query, (product_sku,))

            if not price_result:
                return False

            unit_price = price_result[0]['price']

            check_query = """
            SELECT order_item_id, quantity FROM order_items 
            WHERE order_id = %s AND product_id = %s
            """
            existing = self.execute_query(check_query, (order_id, product_sku))

            if existing:
                update_query = """
                UPDATE order_items 
                SET quantity = quantity + %s, unit_price = %s
                WHERE order_id = %s AND product_id = %s
                """
                result = self.execute_update(update_query, (quantity, unit_price, order_id, product_sku))
                return result > 0
            else:
                insert_query = """
                INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
                """
                result = self.execute_update(insert_query, (order_id, product_sku, quantity, unit_price))
                return result > 0

        except Exception:
            return False

    def remove_order_item(self, order_id: int, product_sku: str) -> bool:
        query = "DELETE FROM order_items WHERE order_id = %s AND product_id = %s"
        return self.execute_update(query, (order_id, product_sku)) > 0

    def get_order_items(self, order_id: int) -> List[Dict[str, Any]]:
        query = """
        SELECT 
            oi.product_id as sku, 
            oi.quantity, 
            oi.unit_price,
            p.name, 
            p.price, 
            p.unit,
            (oi.quantity * oi.unit_price) as total_price
        FROM order_items oi
        LEFT JOIN products p ON oi.product_id = p.sku
        WHERE oi.order_id = %s
        ORDER BY oi.order_item_id
        """
        return self.execute_query(query, (order_id,))

    def get_user_by_credentials(self, login: str, password: str) -> Optional[Dict[str, Any]]:
        query = """
        SELECT u.user_id, u.login, u.full_name, u.role_id, r.role_name
        FROM users u
        JOIN roles r ON u.role_id = r.role_id
        WHERE u.login = %s AND u.password_hash = %s
        """
        result = self.execute_query(query, (login, password))
        return result[0] if result else None

    def get_all_users(self) -> List[Dict[str, Any]]:
        query = """
        SELECT u.user_id, u.login, u.full_name, u.role_id, r.role_name
        FROM users u
        JOIN roles r ON u.role_id = r.role_id
        ORDER BY u.full_name
        """
        return self.execute_query(query)

    def get_users_by_role(self, role_name: str) -> List[Dict[str, Any]]:
        query = """
        SELECT u.user_id, u.login, u.full_name, u.role_id, r.role_name
        FROM users u
        JOIN roles r ON u.role_id = r.role_id
        WHERE r.role_name = %s
        ORDER BY u.full_name
        """
        return self.execute_query(query, (role_name,))

    def get_all_warehouses(self) -> List[Dict[str, Any]]:
        query = "SELECT warehouse_id, address FROM warehouses ORDER BY address"
        return self.execute_query(query)

    def get_warehouse_by_id(self, warehouse_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT warehouse_id, address FROM warehouses WHERE warehouse_id = %s"
        result = self.execute_query(query, (warehouse_id,))
        return result[0] if result else None

    def get_warehouse_addresses(self) -> List[str]:
        query = "SELECT address FROM warehouses ORDER BY address"
        result = self.execute_query(query)
        return [row['address'] for row in result]

    def get_all_categories(self) -> List[str]:
        query = "SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category"
        result = self.execute_query(query)
        return [row['category'] for row in result]

    def get_all_suppliers(self) -> List[str]:
        query = "SELECT DISTINCT supplier FROM products WHERE supplier IS NOT NULL ORDER BY supplier"
        result = self.execute_query(query)
        return [row['supplier'] for row in result]

    def get_all_manufacturers(self) -> List[str]:
        query = "SELECT DISTINCT manufacturer FROM products WHERE manufacturer IS NOT NULL ORDER BY manufacturer"
        result = self.execute_query(query)
        return [row['manufacturer'] for row in result]

    def get_all_order_statuses(self) -> List[str]:
        return [
            "Новый",
            "В обработке",
            "Собран",
            "Передан в доставку",
            "Доставлен",
            "Готов к выдаче",
            "Выдан",
            "Отменен"
        ]

    def get_products_low_stock(self, threshold: int = 10) -> List[Dict[str, Any]]:
        query = """
        SELECT sku, name, quantity, unit, price, category
        FROM products
        WHERE quantity <= %s
        ORDER BY quantity, sku
        """
        return self.execute_query(query, (threshold,))

    def get_orders_by_status(self, status: str) -> List[Dict[str, Any]]:
        query = """
        SELECT o.order_id, o.order_date, o.delivery_date, 
               w.address as delivery_point, o.pickup_code, o.status,
               u.full_name as customer_name
        FROM orders o
        LEFT JOIN warehouses w ON o.warehouse_id = w.warehouse_id
        LEFT JOIN users u ON o.customer_id = u.user_id
        WHERE o.status = %s
        ORDER BY o.order_date
        """
        return self.execute_query(query, (status,))

    def get_top_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
        SELECT p.sku, p.name, p.category, p.price,
               SUM(oi.quantity) as total_sold,
               COUNT(DISTINCT oi.order_id) as order_count
        FROM order_items oi
        JOIN products p ON oi.product_id = p.sku
        GROUP BY p.sku, p.name, p.category, p.price
        ORDER BY total_sold DESC
        LIMIT %s
        """
        return self.execute_query(query, (limit,))

    def get_orders_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        query = """
        SELECT o.order_id, o.order_date, o.delivery_date, 
               w.address as delivery_point, o.pickup_code, o.status,
               u.full_name as customer_name,
               (SELECT SUM(oi.quantity) FROM order_items oi WHERE oi.order_id = o.order_id) as total_items
        FROM orders o
        LEFT JOIN warehouses w ON o.warehouse_id = w.warehouse_id
        LEFT JOIN users u ON o.customer_id = u.user_id
        WHERE o.order_date BETWEEN %s AND %s
        ORDER BY o.order_date
        """
        return self.execute_query(query, (start_date, end_date))

    def test_connection(self) -> bool:
        try:
            result = self.execute_query("SELECT 1 as test")
            return bool(result)
        except:
            return False

    def get_database_info(self) -> Dict[str, Any]:
        try:
            tables_query = """
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns 
                    WHERE table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public'
            ORDER BY table_name
            """

            tables = self.execute_query(tables_query)

            stats = {
                'products': len(self.get_all_products()),
                'orders': len(self.get_all_orders()),
                'users': len(self.get_all_users()),
                'warehouses': len(self.get_all_warehouses()),
                'tables': tables
            }

            return stats
        except Exception:
            return {}

db = Database()