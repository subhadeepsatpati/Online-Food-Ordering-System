import sqlite3

DATABASE = "food_delivery.db"


# ==========================================
# CREATE DATABASE
# ==========================================

def create_database():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # ==========================================
    # USERS TABLE
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            phone TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            address TEXT NOT NULL,

            is_verified INTEGER DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


    # ==========================================
    # RESTAURANTS TABLE
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            description TEXT,

            location TEXT,

            phone TEXT,

            image TEXT,

            rating REAL DEFAULT 0,

            is_active INTEGER DEFAULT 1,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


    # ==========================================
    # MENU ITEMS TABLE
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            restaurant_id INTEGER NOT NULL,

            name TEXT NOT NULL,

            description TEXT,

            price REAL NOT NULL,

            category TEXT,

            image TEXT,

            is_available INTEGER DEFAULT 1,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (restaurant_id)
                REFERENCES restaurants(id),

            UNIQUE (restaurant_id, name)
        )
    """)


    # ==========================================
    # CARTS TABLE
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
    """)


    # ==========================================
    # CART ITEMS TABLE
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart_items (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            cart_id INTEGER NOT NULL,

            menu_item_id INTEGER NOT NULL,

            quantity INTEGER NOT NULL DEFAULT 1,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (cart_id)
                REFERENCES carts(id),

            FOREIGN KEY (menu_item_id)
                REFERENCES menu_items(id),

            UNIQUE (cart_id, menu_item_id)
        )
    """)

    # ==========================================
    # CREATE ORDERS TABLE
    # ==========================================
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
    
            id INTEGER PRIMARY KEY AUTOINCREMENT,
    
            user_id INTEGER NOT NULL,
    
            delivery_address TEXT NOT NULL,
    
            payment_method TEXT NOT NULL,
    
            subtotal REAL NOT NULL,
    
            delivery_fee REAL NOT NULL,
    
            total_amount REAL NOT NULL,
    
            status TEXT DEFAULT 'Placed',
    
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
            FOREIGN KEY (user_id)
            REFERENCES users(id)
        )
    """)


    # ==========================================
    # CREATE ORDER ITEMS TABLE
    # ==========================================
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
    
            id INTEGER PRIMARY KEY AUTOINCREMENT,
    
            order_id INTEGER NOT NULL,
    
            menu_item_id INTEGER NOT NULL,
    
            item_name TEXT NOT NULL,
    
            price REAL NOT NULL,
    
            quantity INTEGER NOT NULL,
    
            subtotal REAL NOT NULL,
    
            FOREIGN KEY (order_id)
            REFERENCES orders(id)
        )
    """)
    

    # ==========================================
    # COMMIT & CLOSE
    # ==========================================

    connection.commit()
    connection.close()


# ==========================================
# CHECK USER EXISTS
# ==========================================

def user_exists(email, phone):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM users
        WHERE email = ? OR phone = ?
    """, (email, phone))

    user = cursor.fetchone()

    connection.close()

    return user is not None


# ==========================================
# REGISTER USER
# ==========================================

def register_user(
    name,
    email,
    phone,
    password_hash,
    address
):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO users
            (
                name,
                email,
                phone,
                password_hash,
                address
            )

            VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            email,
            phone,
            password_hash,
            address
        ))

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


# ==========================================
# GET USER BY EMAIL
# ==========================================

def get_user_by_email(email):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            phone,
            password_hash,
            address,
            is_verified
        FROM users
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()

    connection.close()

    return user


# ==========================================
# ADD RESTAURANT
# ==========================================

def add_restaurant(
    name,
    description,
    location,
    phone,
    image,
    rating
):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO restaurants
            (
                name,
                description,
                location,
                phone,
                image,
                rating
            )

            VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            description,
            location,
            phone,
            image,
            rating
        ))

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


# ==========================================
# GET ALL RESTAURANTS
# ==========================================

def get_all_restaurants():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            description,
            location,
            phone,
            image,
            rating
        FROM restaurants
        WHERE is_active = 1
        ORDER BY rating DESC
    """)

    restaurants = cursor.fetchall()

    connection.close()

    return restaurants


# ==========================================
# GET RESTAURANT BY ID
# ==========================================

def get_restaurant_by_id(restaurant_id):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            description,
            location,
            phone,
            image,
            rating
        FROM restaurants
        WHERE id = ?
          AND is_active = 1
    """, (restaurant_id,))

    restaurant = cursor.fetchone()

    connection.close()

    return restaurant


# ==========================================
# ADD MENU ITEM
# ==========================================

def add_menu_item(
    restaurant_id,
    name,
    description,
    price,
    category,
    image
):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT OR IGNORE INTO menu_items
            (
                restaurant_id,
                name,
                description,
                price,
                category,
                image
            )

            VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            restaurant_id,
            name,
            description,
            price,
            category,
            image
        ))

        connection.commit()

        return True

    except sqlite3.Error:

        return False

    finally:

        connection.close()


# ==========================================
# GET MENU ITEMS
# ==========================================

def get_menu_items(restaurant_id):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            restaurant_id,
            name,
            description,
            price,
            category,
            image
        FROM menu_items
        WHERE restaurant_id = ?
          AND is_available = 1
        ORDER BY category, name
    """, (restaurant_id,))

    menu_items = cursor.fetchall()

    connection.close()

    return menu_items


# ==========================================
# UPDATE MENU ITEM IMAGE
# ==========================================

def update_menu_item_image(menu_item_id, image):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE menu_items
            SET image = ?
            WHERE id = ?
        """,
        (
            image,
            menu_item_id
        ))

        connection.commit()

        return True

    except sqlite3.Error:

        return False

    finally:

        connection.close()


# ==========================================
# GET OR CREATE CART
# ==========================================

def get_or_create_cart(user_id):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM carts
        WHERE user_id = ?
    """, (user_id,))

    cart = cursor.fetchone()

    if cart:

        cart_id = cart[0]

    else:

        cursor.execute("""
            INSERT INTO carts (user_id)
            VALUES (?)
        """, (user_id,))

        connection.commit()

        cart_id = cursor.lastrowid

    connection.close()

    return cart_id


# ==========================================
# ADD ITEM TO CART
# ==========================================

def add_to_cart(user_id, menu_item_id):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM carts
        WHERE user_id = ?
    """, (user_id,))

    cart = cursor.fetchone()

    if cart:

        cart_id = cart[0]

    else:

        cursor.execute("""
            INSERT INTO carts (user_id)
            VALUES (?)
        """, (user_id,))

        cart_id = cursor.lastrowid

    cursor.execute("""
        SELECT id, quantity
        FROM cart_items
        WHERE cart_id = ?
          AND menu_item_id = ?
    """, (cart_id, menu_item_id))

    item = cursor.fetchone()

    if item:

        cursor.execute("""
            UPDATE cart_items
            SET quantity = quantity + 1
            WHERE id = ?
        """, (item[0],))

    else:

        cursor.execute("""
            INSERT INTO cart_items
            (
                cart_id,
                menu_item_id,
                quantity
            )
            VALUES (?, ?, 1)
        """, (cart_id, menu_item_id))

    connection.commit()

    connection.close()

    return True


# ==========================================
# GET CART ITEMS
# ==========================================

def get_cart_items(user_id):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            cart_items.id,
            menu_items.name,
            menu_items.description,
            menu_items.price,
            menu_items.image,
            cart_items.quantity,
            menu_items.price * cart_items.quantity AS subtotal,
            menu_items.id AS real_menu_item_id
        FROM cart_items
        INNER JOIN carts
            ON cart_items.cart_id = carts.id
        INNER JOIN menu_items
            ON cart_items.menu_item_id = menu_items.id
        WHERE carts.user_id = ?
        ORDER BY cart_items.id DESC
    """, (user_id,))

    items = cursor.fetchall()

    connection.close()

    return items


# ==========================================
# GET CART TOTAL
# ==========================================

def get_cart_total(user_id):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COALESCE(
                SUM(
                    menu_items.price *
                    cart_items.quantity
                ),
                0
            )
        FROM cart_items
        INNER JOIN carts
            ON cart_items.cart_id = carts.id
        INNER JOIN menu_items
            ON cart_items.menu_item_id = menu_items.id
        WHERE carts.user_id = ?
    """, (user_id,))

    total = cursor.fetchone()[0]

    connection.close()

    return total


# ==========================================
# UPDATE CART ITEM QUANTITY
# ==========================================

def update_cart_quantity(cart_item_id, user_id, quantity):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    if quantity <= 0:

        cursor.execute("""
            DELETE FROM cart_items
            WHERE id = ?
            AND cart_id IN (
                SELECT id
                FROM carts
                WHERE user_id = ?
            )
        """, (
            cart_item_id,
            user_id
        ))

    else:

        cursor.execute("""
            UPDATE cart_items
            SET quantity = ?
            WHERE id = ?
            AND cart_id IN (
                SELECT id
                FROM carts
                WHERE user_id = ?
            )
        """, (
            quantity,
            cart_item_id,
            user_id
        ))

    connection.commit()

    connection.close()


# ==========================================
# REMOVE CART ITEM
# ==========================================

def remove_cart_item(cart_item_id, user_id):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM cart_items
        WHERE id = ?
        AND cart_id IN (
            SELECT id
            FROM carts
            WHERE user_id = ?
        )
    """, (
        cart_item_id,
        user_id
    ))

    connection.commit()

    connection.close()


# ==========================================
# CREATE ORDER
# ==========================================

def create_order(
    user_id,
    delivery_address,
    payment_method,
    subtotal,
    delivery_fee,
    total_amount,
    cart_items
):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO orders
            (
                user_id,
                delivery_address,
                payment_method,
                subtotal,
                delivery_fee,
                total_amount
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            delivery_address,
            payment_method,
            subtotal,
            delivery_fee,
            total_amount
        ))

        order_id = cursor.lastrowid

        for item in cart_items:

            cursor.execute("""
                INSERT INTO order_items
                (
                    order_id,
                    menu_item_id,
                    item_name,
                    price,
                    quantity,
                    subtotal
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                order_id,
                item[7],  # Uses real_menu_item_id
                item[1],
                item[3],
                item[5],
                item[6]
            ))

        cursor.execute("""
            DELETE FROM cart_items
            WHERE cart_id IN (
                SELECT id
                FROM carts
                WHERE user_id = ?
            )
        """, (user_id,))

        connection.commit()

        return order_id

    except Exception:

        connection.rollback()

        return None

    finally:

        connection.close()


# ==========================================
# SYNC ALL MENU IMAGES (BULK UPDATE)
# ==========================================

def sync_all_menu_images():

    image_mappings = {
        "Chicken Burger": "/static/images/chicken-burger.jpg",
        "Chicken Roll": "/static/images/chicken-roll.jpg",
        "French Fries": "/static/images/french-fries.jpg",
        "Chicken Biryani": "/static/images/chicken-biryani.jpg",
        "Mutton Biryani": "/static/images/mutton-biryani.jpg",
        "Chicken Pizza": "/static/images/chicken-pizza.jpg",
        "Veg Pizza": "/static/images/veg-pizza.jpg",
        "Garlic Bread": "/static/images/garlic-bread.jpg"
    }

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    try:

        for item_name, path in image_mappings.items():

            cursor.execute("""
                UPDATE menu_items
                SET image = ?
                WHERE name = ?
            """, (path, item_name))

        connection.commit()

        print("All menu item image paths updated successfully!")

    except Exception as e:

        connection.rollback()

        print(f"Error updating images: {e}")

    finally:

        connection.close()


# ==========================================
# EXECUTE IMAGE SYNC ON DIRECT RUN
# ==========================================

if __name__ == "__main__":
    sync_all_menu_images()