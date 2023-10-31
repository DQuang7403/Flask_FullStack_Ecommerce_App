from flask import Blueprint, render_template

views = Blueprint("views", __name__)

@views.route('/')
def home():
  return render_template('home.html')

@views.route('/account')
def account():
  return render_template('account.html')

@views.route('/cart')
def shopping_cart():
  return render_template('cart.html')

@views.route('/all_products')
def all_products():
  return render_template('all_products.html')