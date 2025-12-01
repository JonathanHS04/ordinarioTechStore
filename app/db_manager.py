import psycopg2
from pymongo import MongoClient
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class DBManager:
    def __init__(self):
        self.pg_host = os.getenv('PG_HOST', 'localhost')
        self.pg_db = os.getenv('PG_DB', 'postgres')
        self.pg_user = os.getenv('PG_USER', 'app_role')
        self.pg_pass = os.getenv('PG_PASS', 'app_secure_pass')
        
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://appUser:appPassword123@localhost:27017/ecommerce_db?authSource=ecommerce_db')
        self.mongo_db_name = os.getenv('MONGO_DB_NAME', 'ecommerce_db')
        self.client = MongoClient(self.mongo_uri)

    def get_pg_connection(self):
        return psycopg2.connect(
            host=self.pg_host,
            database=self.pg_db,
            user=self.pg_user,
            password=self.pg_pass
        )

    def get_mongo_db(self):
        return self.client[self.mongo_db_name]

    def create_order(self, user_id, items, total_amount):
        """
        Transacción distribuida simulada (Saga Pattern simplificado)
        1. Verificar Stock en Mongo
        2. Crear Orden en Postgres
        3. Reducir Stock en Mongo
        Si falla paso 3, hacer rollback de paso 2.
        """
        pg_conn = self.get_pg_connection()
        mongo_db = self.get_mongo_db()
        
        try:
            for item in items:
                product = mongo_db.products.find_one({"_id": item['product_id']})
                if not product or product['stock'] < item['quantity']:
                    raise Exception(f"Stock insuficiente para producto {item['product_id']}")

            pg_cursor = pg_conn.cursor()
            pg_cursor.execute(
                "INSERT INTO orders (user_id, total_amount, status) VALUES (%s, %s, 'pending') RETURNING order_id",
                (user_id, total_amount)
            )
            order_id = pg_cursor.fetchone()[0]
            
            for item in items:
                pg_cursor.execute(
                    "INSERT INTO order_items (order_id, product_id_mongo, quantity, unit_price) VALUES (%s, %s, %s, %s)",
                    (order_id, str(item['product_id']), item['quantity'], item['price'])
                )
            
            for item in items:
                result = mongo_db.products.update_one(
                    {"_id": item['product_id'], "stock": {"$gte": item['quantity']}},
                    {"$inc": {"stock": -item['quantity']}}
                )
                if result.modified_count == 0:
                    raise Exception("Error de concurrencia al actualizar stock en Mongo")

            pg_conn.commit()
            
            mongo_db.audit_logs.insert_one({
                "action": "create_order",
                "order_id": order_id,
                "user_id": user_id,
                "timestamp": datetime.now(),
                "status": "success"
            })
            
            return order_id

        except Exception as e:
            pg_conn.rollback()
            print(f"Error en transacción: {e}")
            raise e
        finally:
            pg_conn.close()

    def get_products(self):
        db = self.get_mongo_db()
        return list(db.products.find())

    def get_orders(self):
        conn = self.get_pg_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders")
        columns = [desc[0] for desc in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]
        conn.close()
        return results

    def authenticate_user(self, username, password):
        """Authenticate user with username and password"""
        conn = self.get_pg_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, password_hash, email, role FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            return {
                'user_id': user[0],
                'username': user[1],
                'email': user[3],
                'role': user[4]
            }
        return None

    def create_user(self, username, email, password, role='client'):
        """Create a new user"""
        conn = self.get_pg_connection()
        cur = conn.cursor()
        password_hash = generate_password_hash(password)
        
        try:
            cur.execute(
                "INSERT INTO users (username, password_hash, email, role) VALUES (%s, %s, %s, %s) RETURNING user_id",
                (username, password_hash, email, role)
            )
            user_id = cur.fetchone()[0]
            conn.commit()
            return user_id
        except psycopg2.IntegrityError as e:
            conn.rollback()
            raise Exception("El nombre de usuario o email ya existe")
        finally:
            conn.close()

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_pg_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, email, role FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        conn.close()
        
        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[3]
            }
        return None

    def get_user_by_username(self, username):
        """Get user by username"""
        conn = self.get_pg_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, email, role FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        conn.close()
        
        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[3]
            }
        return None

    def get_user_orders(self, user_id):
        """Get all orders for a specific user"""
        conn = self.get_pg_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        columns = [desc[0] for desc in cur.description]
        results = [dict(zip(columns, row)) for row in cur.fetchall()]
        conn.close()
        return results

    def get_order_details(self, order_id):
        """Get order details including items"""
        conn = self.get_pg_connection()
        mongo_db = self.get_mongo_db()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
        columns = [desc[0] for desc in cur.description]
        order = cur.fetchone()
        
        if not order:
            conn.close()
            return None
        
        order_dict = dict(zip(columns, order))
        
        cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
        item_columns = [desc[0] for desc in cur.description]
        items = [dict(zip(item_columns, row)) for row in cur.fetchall()]
        
        for item in items:
            from bson.objectid import ObjectId
            product = mongo_db.products.find_one({"_id": ObjectId(item['product_id_mongo'])})
            if product:
                item['product_name'] = product['name']
                item['product_category'] = product.get('category', 'N/A')
        
        order_dict['order_items'] = items
        conn.close()
        return order_dict

    def cancel_order(self, order_id):
        """Cancel order and restore stock"""
        conn = self.get_pg_connection()
        cur = conn.cursor()
        mongo_db = self.get_mongo_db()
        
        try:
            # 1. Get order items to restore stock
            cur.execute("SELECT product_id_mongo, quantity FROM order_items WHERE order_id = %s", (order_id,))
            items = cur.fetchall()
            
            # 2. Update status in Postgres
            cur.execute(
                "UPDATE orders SET status = 'cancelled' WHERE order_id = %s",
                (order_id,)
            )
            
            # 3. Restore stock in Mongo
            from bson.objectid import ObjectId
            for item in items:
                product_id = item[0]
                quantity = item[1]
                mongo_db.products.update_one(
                    {"_id": ObjectId(product_id)},
                    {"$inc": {"stock": quantity}}
                )
            
            conn.commit()
            
            # Log audit
            mongo_db.audit_logs.insert_one({
                "action": "cancel_order",
                "order_id": order_id,
                "timestamp": datetime.now(),
                "status": "success"
            })
            
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def update_order_status(self, order_id, new_status):
        """Update order status"""
        conn = self.get_pg_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                "UPDATE orders SET status = %s WHERE order_id = %s",
                (new_status, order_id)
            )
            conn.commit()
            
            mongo_db = self.get_mongo_db()
            mongo_db.audit_logs.insert_one({
                "action": "update_order_status",
                "order_id": order_id,
                "new_status": new_status,
                "timestamp": datetime.now()
            })
            
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def create_payment(self, order_id, amount, payment_method='credit_card'):
        """Create a payment record"""
        conn = self.get_pg_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                "INSERT INTO payments (order_id, amount, payment_method) VALUES (%s, %s, %s) RETURNING payment_id",
                (order_id, amount, payment_method)
            )
            payment_id = cur.fetchone()[0]
            conn.commit()
            return payment_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
