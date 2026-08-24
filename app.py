from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

import bcrypt
import re

from database import (
    create_database,
    update_menu_item_image,
    user_exists,
    register_user,
    get_user_by_email,
    add_restaurant,
    get_all_restaurants,
    get_restaurant_by_id,
    add_menu_item,
    get_menu_items,
    add_to_cart,
    get_cart_items,
    get_cart_total,
    update_cart_quantity,
    remove_cart_item,
    create_order
)

# ==========================================
# FLASK APPLICATION
# ==========================================

app = Flask(__name__)

app.secret_key = "food_delivery_secret_key"


# ==========================================
# CREATE DATABASE
# ==========================================

create_database()


# ==========================================
# EMAIL VALIDATION
# ==========================================

def is_valid_email(email):

    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    return re.match(pattern, email) is not None


# ==========================================
# PHONE VALIDATION
# ==========================================

def is_valid_phone(phone):

    # Indian mobile number
    # Starts with 6, 7, 8 or 9
    # Exactly 10 digits

    pattern = r"^[6-9]\d{9}$"

    return re.match(pattern, phone) is not None


# ==========================================
# PASSWORD VALIDATION
# ==========================================

def is_strong_password(password):

    # Minimum 8 characters

    if len(password) < 8:
        return False

    # At least one uppercase letter

    if not re.search(r"[A-Z]", password):
        return False

    # At least one lowercase letter

    if not re.search(r"[a-z]", password):
        return False

    # At least one number

    if not re.search(r"\d", password):
        return False

    # At least one special character

    if not re.search(
        r"[!@#$%^&*(),.?\":{}|<>]",
        password
    ):
        return False

    return True


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# REGISTER
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():

    # --------------------------------------
    # SHOW REGISTRATION PAGE
    # --------------------------------------

    if request.method == "GET":

        return render_template("register.html")


    # --------------------------------------
    # GET FORM DATA
    # --------------------------------------

    name = request.form.get(
        "name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )

    address = request.form.get(
        "address",
        ""
    ).strip()


    # ======================================
    # VALIDATE EMPTY FIELDS
    # ======================================

    if not name or \
       not email or \
       not phone or \
       not password or \
       not address:

        flash(
            "Please fill in all fields.",
            "error"
        )

        return redirect(
            url_for("register")
        )


    # ======================================
    # VALIDATE NAME
    # ======================================

    if len(name) < 2:

        flash(
            "Please enter a valid name.",
            "error"
        )

        return redirect(
            url_for("register")
        )


    # ======================================
    # VALIDATE EMAIL
    # ======================================

    if not is_valid_email(email):

        flash(
            "Please enter a valid email address.",
            "error"
        )

        return redirect(
            url_for("register")
        )


    # ======================================
    # VALIDATE PHONE
    # ======================================

    if not is_valid_phone(phone):

        flash(
            "Please enter a valid 10-digit Indian mobile number.",
            "error"
        )

        return redirect(
            url_for("register")
        )


    # ======================================
    # CHECK PASSWORD MATCH
    # ======================================

    if password != confirm_password:

        flash(
            "Passwords do not match.",
            "error"
        )

        return redirect(
            url_for("register")
        )


    # ======================================
    # CHECK PASSWORD STRENGTH
    # ======================================

    if not is_strong_password(password):

        flash(
            "Password must contain at least 8 characters, "
            "one uppercase letter, "
            "one lowercase letter, "
            "one number and "
            "one special character.",
            "error"
        )

        return redirect(
            url_for("register")
        )


    # ======================================
    # CHECK DUPLICATE USER
    # ======================================

    if user_exists(email, phone):

        flash(
            "Email or mobile number is already registered.",
            "error"
        )

        return redirect(
            url_for("register")
        )


    # ======================================
    # BCRYPT PASSWORD HASHING
    # ======================================

    password_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt()

    password_hash = bcrypt.hashpw(
        password_bytes,
        salt
    )

    password_hash = password_hash.decode("utf-8")


    # ======================================
    # SAVE USER
    # ======================================

    success = register_user(
        name,
        email,
        phone,
        password_hash,
        address
    )


    # ======================================
    # REGISTRATION RESULT
    # ======================================

    if success:

        flash(
            "Registration successful!",
            "success"
        )

        return redirect(
            url_for("register")
        )

    else:

        flash(
            "Registration failed. Please try again.",
            "error"
        )

        return redirect(
            url_for("register")
        )

# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    # --------------------------------------
    # SHOW LOGIN PAGE
    # --------------------------------------

    if request.method == "GET":

        return render_template("login.html")


    # --------------------------------------
    # GET FORM DATA
    # --------------------------------------

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )


    # --------------------------------------
    # CHECK EMPTY FIELDS
    # --------------------------------------

    if not email or not password:

        flash(
            "Please enter email and password.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    # --------------------------------------
    # FIND USER
    # --------------------------------------

    user = get_user_by_email(email)


    # --------------------------------------
    # USER NOT FOUND
    # --------------------------------------

    if user is None:

        flash(
            "Invalid email or password.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    # --------------------------------------
    # GET PASSWORD HASH
    # --------------------------------------

    stored_password_hash = user[4]


    # --------------------------------------
    # CHECK PASSWORD
    # --------------------------------------

    password_correct = bcrypt.checkpw(
        password.encode("utf-8"),
        stored_password_hash.encode("utf-8")
    )


    # --------------------------------------
    # WRONG PASSWORD
    # --------------------------------------

    if not password_correct:

        flash(
            "Invalid email or password.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    # --------------------------------------
    # CREATE LOGIN SESSION
    # --------------------------------------

    session["user_id"] = user[0]

    session["user_name"] = user[1]

    session["user_email"] = user[2]


    # --------------------------------------
    # LOGIN SUCCESS
    # --------------------------------------

    flash(
        "Login successful!",
        "success"
    )

    return redirect(
        url_for("home")
    )


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    # Remove all login information
    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(
        url_for("home")
    )


# ==========================================
# PROFILE
# ==========================================

@app.route("/profile")
def profile():

    # Check if user is logged in

    if "user_id" not in session:

        flash(
            "Please login to access your profile.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    # User is logged in

    return render_template(
        "profile.html"
    )

# ==========================================
# RESTAURANTS
# ==========================================

@app.route("/restaurants")
def restaurants():

    restaurant_list = get_all_restaurants()

    return render_template(
        "restaurants.html",
        restaurants=restaurant_list
    )


# ==========================================
# TEMPORARY RESTAURANT DATA
# ==========================================

@app.route("/add-test-restaurants")
def add_test_restaurants():

    restaurants = [

        (
            "Spice Garden",
            "Authentic Indian food and delicious biryani.",
            "Kolkata",
            "9876543210",
            "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",
            4.5
        ),

        (
            "Pizza Palace",
            "Fresh pizzas, burgers and Italian food.",
            "Kolkata",
            "9876543211",
            "https://images.unsplash.com/photo-1579751626657-72bc17010498",
            4.3
        ),

        (
            "Food Junction",
            "Delicious fast food and refreshing beverages.",
            "Kolkata",
            "9876543212",
            "https://images.unsplash.com/photo-1555396273-367ea4eb4db5",
            4.7
        )

    ]


    for restaurant in restaurants:

        add_restaurant(
            restaurant[0],
            restaurant[1],
            restaurant[2],
            restaurant[3],
            restaurant[4],
            restaurant[5]
        )


    return redirect(
        url_for("restaurants")
    )

# ==========================================
# RESTAURANT MENU
# ==========================================

@app.route("/restaurant/<int:restaurant_id>")
def restaurant_menu(restaurant_id):

    # --------------------------------------
    # GET RESTAURANT
    # --------------------------------------

    restaurant = get_restaurant_by_id(
        restaurant_id
    )


    # --------------------------------------
    # RESTAURANT NOT FOUND
    # --------------------------------------

    if restaurant is None:

        flash(
            "Restaurant not found.",
            "error"
        )

        return redirect(
            url_for("restaurants")
        )


    # --------------------------------------
    # GET MENU ITEMS
    # --------------------------------------

    menu_items = get_menu_items(
        restaurant_id
    )


    # --------------------------------------
    # SHOW MENU
    # --------------------------------------

    return render_template(
        "menu.html",
        restaurant=restaurant,
        menu_items=menu_items
    )


# ==========================================
# TEMPORARY TEST MENU DATA
# ==========================================

@app.route("/add-test-menu")
def add_test_menu():

    test_menu = [

        # ----------------------------------
        # SPICE GARDEN
        # ----------------------------------

        (
            1,
            "Chicken Biryani",
            "Aromatic basmati rice with spicy chicken.",
            180,
            "Biryani",
            "/static/images/chicken-biryani.jpg"
        ),

        (
            1,
            "Mutton Biryani",
            "Traditional mutton biryani with rich spices.",
            250,
            "Biryani",
            "/static/images/mutton-biryani.jpg"
        ),

        (
            1,
            "Chicken Roll",
            "Soft roll filled with spicy chicken.",
            120,
            "Rolls",
            "/static/images/chicken-roll.jpg"
        ),


        # ----------------------------------
        # PIZZA PALACE
        # ----------------------------------

        (
            2,
            "Chicken Pizza",
            "Cheesy pizza topped with chicken.",
            250,
            "Pizza",
            "/static/images/chicken-pizza.jpg"
        ),

        (
            2,
            "Veg Pizza",
            "Fresh vegetables with mozzarella cheese.",
            220,
            "Pizza",
            "/static/images/veg-pizza.jpg"
        ),

        (
            2,
            "Garlic Bread",
            "Crispy garlic bread with cheese.",
            140,
            "Sides",
            "/static/images/garlic-bread.jpg"
        ),


        # ----------------------------------
        # FOOD JUNCTION
        # ----------------------------------

        (
            3,
            "Chicken Burger",
            "Juicy chicken burger with fresh vegetables.",
            150,
            "Burger",
            "/static/images/chicken-burger.jpg"
        ),

        (
            3,
            "French Fries",
            "Crispy golden french fries.",
            100,
            "Sides",
            "/static/images/french-fries.jpg"
        ),

        (
            3,
            "Chicken Roll",
            "Delicious spicy chicken roll.",
            120,
            "Rolls",
            "/static/images/chicken-roll.jpg"
        )

    ]


    for item in test_menu:

        add_menu_item(
            item[0],
            item[1],
            item[2],
            item[3],
            item[4],
            item[5]
        )


    return redirect(
        url_for(
            "restaurant_menu",
            restaurant_id=1
        )
    )


# ==========================================
# ADD ITEM TO CART
# ==========================================

@app.route("/add-to-cart/<int:menu_item_id>", methods=["POST"])
def add_item_to_cart(menu_item_id):

    # --------------------------------------
    # CHECK LOGIN
    # --------------------------------------

    if "user_id" not in session:

        flash(
            "Please login to add items to your cart.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    # --------------------------------------
    # GET USER ID
    # --------------------------------------

    user_id = session["user_id"]


    # --------------------------------------
    # ADD ITEM
    # --------------------------------------

    success = add_to_cart(
        user_id,
        menu_item_id
    )


    # --------------------------------------
    # RESULT
    # --------------------------------------

    if success:

        flash(
            "Item added to cart successfully!",
            "success"
        )

    else:

        flash(
            "Unable to add item to cart.",
            "error"
        )


    # --------------------------------------
    # RETURN TO PREVIOUS PAGE
    # --------------------------------------

    return redirect(
        request.referrer or
        url_for("restaurants")
    )

# ==========================================
# CART PAGE
# ==========================================

@app.route("/cart")
def cart():

    # Check login

    if "user_id" not in session:

        flash(
            "Please login to view your cart.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    # Get logged-in user

    user_id = session["user_id"]


    # Get cart items

    cart_items = get_cart_items(
        user_id
    )


    # Get total

    cart_total = get_cart_total(
        user_id
    )


    return render_template(
        "cart.html",
        cart_items=cart_items,
        cart_total=cart_total
    )

# ==========================================
# UPDATE CART QUANTITY
# ==========================================

@app.route(
    "/update-cart/<int:cart_item_id>",
    methods=["POST"]
)
def update_cart(cart_item_id):

    # Check login

    if "user_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    user_id = session["user_id"]


    # Get requested quantity

    quantity = request.form.get(
        "quantity",
        type=int
    )


    if quantity is None or quantity < 1:

        quantity = 1


    update_cart_quantity(
        cart_item_id,
        user_id,
        quantity
    )


    return redirect(
        url_for("cart")
    )

# ==========================================
# REMOVE CART ITEM
# ==========================================

@app.route(
    "/remove-cart-item/<int:cart_item_id>",
    methods=["POST"]
)
def remove_cart_item_route(cart_item_id):

    # Check login

    if "user_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    user_id = session["user_id"]


    remove_cart_item(
        cart_item_id,
        user_id
    )


    flash(
        "Item removed from cart.",
        "success"
    )


    return redirect(
        url_for("cart")
    )


# ==========================================
# CHECKOUT
# ==========================================

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    # --------------------------------------
    # CHECK LOGIN
    # --------------------------------------

    if "user_id" not in session:

        flash(
            "Please login before checkout.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    user_id = session["user_id"]


    # --------------------------------------
    # GET CART
    # --------------------------------------

    cart_items = get_cart_items(
        user_id
    )


    # --------------------------------------
    # EMPTY CART
    # --------------------------------------

    if not cart_items:

        flash(
            "Your cart is empty.",
            "error"
        )

        return redirect(
            url_for("restaurants")
        )


    # --------------------------------------
    # TOTAL
    # --------------------------------------

    subtotal = get_cart_total(
        user_id
    )

    delivery_fee = 40

    total_amount = (
        subtotal +
        delivery_fee
    )


    # --------------------------------------
    # GET USER ADDRESS
    # --------------------------------------

    user = get_user_by_email(
        session["user_email"]
    )

    address = user[5]


    # --------------------------------------
    # SHOW CHECKOUT
    # --------------------------------------

    if request.method == "GET":

        return render_template(
            "checkout.html",

            cart_items=cart_items,

            subtotal=subtotal,

            delivery_fee=delivery_fee,

            total_amount=total_amount,

            address=address
        )


    # --------------------------------------
    # GET FORM DATA
    # --------------------------------------

    delivery_address = request.form.get(
        "delivery_address",
        ""
    ).strip()

    payment_method = request.form.get(
        "payment_method",
        ""
    ).strip()


    # --------------------------------------
    # VALIDATE ADDRESS
    # --------------------------------------

    if not delivery_address:

        flash(
            "Please enter your delivery address.",
            "error"
        )

        return redirect(
            url_for("checkout")
        )


    # --------------------------------------
    # VALIDATE PAYMENT
    # --------------------------------------

    if payment_method not in [
        "Cash on Delivery",
        "UPI",
        "Card"
    ]:

        flash(
            "Please select a valid payment method.",
            "error"
        )

        return redirect(
            url_for("checkout")
        )


    # --------------------------------------
    # CREATE ORDER
    # --------------------------------------

    order_id = create_order(

        user_id,

        delivery_address,

        payment_method,

        subtotal,

        delivery_fee,

        total_amount,

        cart_items
    )


    # --------------------------------------
    # ORDER FAILED
    # --------------------------------------

    if order_id is None:

        flash(
            "Unable to place order. Please try again.",
            "error"
        )

        return redirect(
            url_for("checkout")
        )


    # --------------------------------------
    # ORDER SUCCESS
    # --------------------------------------

    return redirect(
        url_for(
            "order_success",
            order_id=order_id
        )
    )

# ==========================================
# ORDER SUCCESS
# ==========================================

@app.route("/order-success/<int:order_id>")
def order_success(order_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    return render_template(
        "order_success.html",
        order_id=order_id
    )

@app.route("/update-chicken-roll-image")
def update_chicken_roll_image():

    success = update_menu_item_image(
        9,
        "/static/images/chicken-roll.jpg"
    )

    if success:
        return "Chicken Roll image updated successfully!"

    return "Failed to update Chicken Roll image."

# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )