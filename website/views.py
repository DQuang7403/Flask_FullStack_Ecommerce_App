from flask import Blueprint, render_template

views = Blueprint("views", __name__)


@views.route('/')
def home():
    return render_template('home.html')


@views.route('/login')
def account():
    return render_template('login.html')


@views.route('/cart')
def shopping_cart():
    return render_template('cart.html')


@views.route('/all_products')
def all_products():
    return render_template('all_products.html')

@views.route('/product_detail')
def product_detail():
    return render_template('product_detail.html')

@views.route('/about')
def about():
    return render_template('about.html')


@views.route('/contact')
def contact():
    return render_template('contact.html')
