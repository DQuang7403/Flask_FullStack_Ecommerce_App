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
    current_username = ""
    current_cart = []
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    if 'cart' in session:
        current_cart = session.get('cart', [])

    return render_template('cart.html', cart=current_cart,user_name = current_username)

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
    # messages = ("Product added successfully! <br> Current:" +
    #             str(rows) + " products" + "<br/><a class='btn btn-primary' href='/cart'>view cart</a><br/> <a class='btn btn-primary' href='/'>home</a>")
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
@views.route('/proceed_cart',methods = ['POST'] )
def proceed_cart():
    if 'current_user' in session:
        user_id = session['current_user']['id']
        user_email = session['current_user']['email']
    else:
        user_id = 0
    if 'cart' in session:
        current_cart = session.get("cart",[])
    conn = sqlite3.connect(sqldbname)
    cur = conn.cursor()
    status = 1
    cur.execute('INSERT INTO "order" (user_id, user_email,status) VALUES(?, ?, ?)',(user_id,user_email,status))
    order_id = cur.lastrowid
    for product in current_cart:
        product_id = product['id']
        price = product['price']
        quantity = product['quantity']
        cur.execute('INSERT or REPLACE INTO "order_details" (order_id, product_id, price, quantity) VALUES(?,?,?,?)',(order_id,product_id,price,quantity))  
    conn.commit()
    conn.close()
    if 'cart' in session:
        current_cart = session.pop("cart",[])
    else:
        print("No cart in session.")
    order_url = url_for('views.order',order_id = order_id, _external = True)
    return f'Redirecting to order page <a href ="{order_url}">{order_url}</a>'
@views.route('/order/',defaults = {'order_id': None},methods = ['GET'])
@views.route('/order/<int:order_id>/', methods = ['GET'])
def order(order_id):
    user_id = session.get('current_user',{}).get('id')
    if user_id:
        conn = sqlite3.connect(sqldbname)
        cur = conn.cursor()
        if order_id is not None:
            cur.execute('Select * from "order" where id = ? and user_id = ?',(order_id,user_id))
            order = cur.fetchone()
            cur.execute('SELECT * from order_details where order_id = ?',(order_id,))
            order_details = cur.fetchall()
            conn.close()
            return render_template('checkout.html',order = order,order_details = order_details)
        else:
            cur.execute('Select * from "order" where user_id = ?',(user_id,))
            user_orders = cur.fetchall()
            conn.close()
            return render_template('orders.html',orders = user_orders)
    return "User not logged in"
@views.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['txt_username']
        password = request.form['txt_password']
        obj_user = get_obj_user(username,password)
        if int(obj_user[0])>0:
            obj_user ={
                "id" : obj_user[0],
                "name": obj_user[1],
                "email":obj_user[2]
            }
            session['current_user'] = obj_user
        return redirect(url_for('views.shopping_cart'))
    return render_template('login.html')

def get_obj_user(username,password):
    result =[]
    conn = sqlite3.connect(sqldbname)
    cur = conn.cursor()
    sqlcommand = "Select * from user where email =? and password = ?"
    cur.execute(sqlcommand,(username,password))
    obj_user = cur.fetchone()
    if len(obj_user)>0:
        result = obj_user
    conn.close()
    return result;
@views.route('/register', methods =['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    username_error = ""
    email_error = ""
    password_error = ""
    if not username: username_error = "Username is required."
    if not password: password_error = "Password is required."
    if not email: email_error = "Email is required."
    if username_error or password_error or email_error:
        return render_template("signup.html", username_error = username_error, password_error =password_error, email_error =email_error, registeration_success = "")
    newid = SaveToDB(username, email, password)
    stroutput = f'Registered: Username: {username},Email: {email}, Password: {password}'
    registeration_success = "Registeration successful with id = "+ str(newid)
    print(registeration_success+stroutput)
    return render_template("signup.html", username_error="", password_error = "", email_error ="", registeration_success = registeration_success+stroutput)
def SaveToDB(name,email,password):
    conn = sqlite3.connect(sqldbname)
    cur = conn.cursor()
    sqlcommand = "SELECT Max(user_id) from user"
    cur.execute(sqlcommand)
    id_max = cur.fetchone()[0]
    id_max = id_max + 1
    cur.execute("INSERT INTO user (user_id, name, email, password) VALUES (?,?,?,?)",(id_max,name,email,password))
    conn.commit()
    conn.close()
    return id_max

