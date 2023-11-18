from flask import Blueprint, render_template, request, session, flash, redirect, url_for
import sqlite3
views = Blueprint("views", __name__)


sqldbname = 'LAPTRINHWEB.db'

@views.context_processor
def my_utility_processor():
    def convert_currency_to_int(currency_str):
        currency_str = currency_str.replace(".", "").replace(" VNĐ", "")
        return int(currency_str)
    def convert_int_to_currency(number):
        number_str = str(number)
        currency_str = ""
        count = 0

        for digit in reversed(number_str):
            if count != 0 and count % 3 == 0:
                currency_str = "." + currency_str
            currency_str = digit + currency_str
            count += 1

        currency_str += " VNĐ"
        return currency_str
    return dict(convert_currency_to_int=convert_currency_to_int, convert_int_to_currency=convert_int_to_currency)

@views.route('/')
def home():
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    sqlcommand = 'SELECT * FROM FASHION LIMIT 0, 4'
    cursor.execute(sqlcommand)
    featuresProduct = cursor.fetchall()
    sqlcommand = 'SELECT * FROM FASHION LIMIT 2, 10'
    cursor.execute(sqlcommand)
    latestProducts = cursor.fetchall()
    return render_template('home.html', featuresProduct=featuresProduct, latestProducts=latestProducts)

@views.route('/cart', methods=['GET'])
def shopping_cart():
    # current_username = ""
    current_cart = []
    # if 'current_user' in session:
    #     current_username = session['current_user']['name']
    # else:
    #     current_username = ""
    if 'cart' in session:
        current_cart = session.get('cart', [])

    return render_template('cart.html', cart=current_cart)
    #user_name = current_username

@views.route('/all_products')
def all_products():
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    sqlcommand = 'SELECT * FROM FASHION'
    cursor.execute(sqlcommand)
    all_products = cursor.fetchall()
    return render_template('all_products.html', all_products=all_products)

@views.route('/product_detail/<id>')
def product_detail(id):
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    sqlcommand = 'SELECT * FROM FASHION WHERE id = ?'
    cursor.execute(sqlcommand, (id,))
    product_detail = cursor.fetchone()
    sqlcommand = 'SELECT * FROM FASHION LIMIT 0, 4'
    cursor.execute(sqlcommand)
    related_products = cursor.fetchall()
    return render_template('product_detail.html', product_detail=product_detail, related_products=related_products)

@views.route('/about')
def about():
    return render_template('about.html')


@views.route('/contact')
def contact():
    return render_template('contact.html')

@views.route('/cart/add', methods=['POST'])
def addToCart():
    productId = request.form['product_id']
    quantity = int(request.form['quantity'])
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT product, price, picture FROM FASHION WHERE id = ?", (productId,))
    product = cursor.fetchone()
    conn.close()
    product_detail = {
        "id": productId,
        "name": product[0],
        "price": product[1],
        "image": product[2],
        "quantity": quantity
    }
    cart = session.get('cart', [])
    found = False
    for item in cart:
        if item["id"] == productId:
            item["quantity"] += quantity
            found = True
            break
    if not found:
        cart.append(product_detail)
    session["cart"] = cart
    rows = len(cart)
    flash('Item added successfully!', 'success')
    return redirect(url_for('views.product_detail', id=productId))

@views.route('/cart/update',methods = ['POST'])
def CartUpdate():
    cart = session.get('cart', [])
    new_cart = []
    for row in cart:
        productId = int(row['id'])
        if f'quantity-{productId}' in request.form:
            quantity = int(request.form[f'quantity-{productId}'])
            if quantity == 0 or f'delete-{productId}' in request.form:
                continue
            row['quantity'] = quantity
        new_cart.append(row)
    session['cart'] = new_cart
    return redirect(url_for('views.shopping_cart'))
#@views.route('proceed_cart',methods = ['POST'] )
#def proceed_cart():
#if 'current_user' in session:
#user_id = session['current_user']['id']
#user_email = session['current_user']['email]
#else:
#user_id = 0

@views.route('/search', methods=['POST'])
def search():
    search_text = request.form['searchInput']
    # username = None
    # if 'current_user' in session:
    #     username = session['current_user']
    if search_text == "":
        flash("You must add some text", "error")
    if search_text != None:
        flash(search_text, 'success')
        conn = sqlite3.connect(sqldbname)
        cursor = conn.cursor()
        sqlcommand = (
            "select * from FASHION where product like '%") + search_text + "%'"
        cursor.execute(sqlcommand)
        data = cursor.fetchall()
        conn.close()
    return render_template('all_products.html', search_text=search_text, all_products=data)