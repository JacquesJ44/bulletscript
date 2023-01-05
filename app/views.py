from crypt import methods
import json
import re
from app import app

#imports of modules
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_session import Session
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

#imports of other helper files
import helperfunctions as hf

#Creating an instance of the SQLAlchemy module to create a class fal
db = SQLAlchemy(app)
Session(app)

# Custom filter for displaying price in Rand with two decimals
app.jinja_env.filters["zar"] = hf.zar

#Creating a class sub_email - table SUB_EMAIL of the db
class Sub_email(db.Model):
    __tablename__ = 'sub_email'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30))
    name = db.Column(db.String(30))
    password = db.Column(db.String(30))
    date_joined = db.Column(db.DateTime)

#Creating a class stock - table STOCK of the db
class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10))
    description = db.Column(db.String(50))
    count = db.Column(db.Integer)
    price = db.Column(db.Float)

#Creating a class cartitem - to create an object of a cart item to add to list   
class Cartitem:
    def __init__(self, id, description, qty, price, total):
        self.id = id
        self.description = description
        self.qty = qty
        self.price = price
        self.total = total

    # This function might not be needed as helperfunctions.py has this already
    def __str__(self):
        return {
            "id" : self.id,
            "description" : self.description,
            "qty" : self.qty,
            "price" : self.price,
            "total" : self.total
        }


# Create an instance of the Mail class
mail = Mail(app)

# print(app.config)

#Display '/' route with GET; save email to database and forward welcome mail on POST
@app.route("/", methods=["GET", "POST"])
def getform():
    #If the user reaches this route via GET then display the webpage
    return render_template('index.html')

# Creating the SIGN UP route
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    # If user clicks the SIGNUP button, render template signup.html
    if request.method == 'GET':
        return render_template('signup.html')

    # If user enter data in the fields - verify the data and save to the db
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        
        # If user does not fill in all the fields
        if not request.form['email'] or not request.form['name'] or not request.form['password'] or not request.form['confirm']:
            flash("Please enter ALL fields", "error")
            return redirect(url_for('signup'))
        
        # If passwords do not match
        if request.form['password'] != request.form['confirm']:
            flash("Passwords do not match", "error")
            return redirect(url_for('signup'))
        
        # If the user already exists redirect to signin.html
        if Sub_email.query.filter_by(email=email).all():
            flash("This account already exists. Please sign in.", "error")
            return redirect(url_for('signin'))
        else:
            # Add new user to bulletscript.db
            hash = generate_password_hash(password)
            
            user = Sub_email(email=email, name=name, password=hash, date_joined=datetime.now())
            db.session.add(user)
            db.session.commit()

            # Mail the contact form information
            msg = Message('Welcome', sender='jjdttesting@gmail.com', recipients=[email], reply_to='jjdttesting@gmail.com')
            msg.body = ('Thank you for subscribing.')
            mail.send(msg)

            # Create a new session for the signed in user
            session['user_id'] = user.id
            session['name'] = user.name
            session['email'] = user.email
            return render_template('index.html')

# Creating the SIGN IN route
@app.route("/signin", methods=['GET', 'POST'])
def signin():
    # Display the SIGN IN page
    if request.method == "GET":
        return render_template('signin.html')

    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        # Ensure that all fields have been filled in
        if not request.form['email'] or not request.form['password']:
            flash("Please enter valid email and password", "Error")
            return redirect(url_for('signin'))

        # Check for the user in the database, log him in and create a new session
        user = Sub_email.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['name'] = user.name
                session['email'] = user.email

                return render_template('index.html')
            else:
                flash("Incorrect username or password", "Error")
                return redirect(url_for('signin'))

        flash("Account does not exist. Please create an account.", "Error")
        return redirect(url_for('signup'))

# Creating the logout route
@app.route('/logout')
def logout():
    # Log the user out and delete the session data
    session['user_id'] = None
    session['name'] = None
    session['email'] = None
    if 'cart' in session:
        session.pop('cart')
    return redirect(url_for('getform'))

# Creating the STORE route
@app.route("/store")
def store():
    return render_template('store.html')

# Display information about the stock item selected and enable the user to buy it. STOCK CODES are stored in the db and are hardcoded in the 'store.html' page to reference them
@app.route("/store/<stock_code>", methods=['GET', 'POST'])
@hf.login_required
def show_items(stock_code):    
    
    stockitem = []

    # Look for the stock code in the db
    item = Stock.query.filter_by(code=stock_code).all()
    
    # If the stock code exists, store all items with that stock code in stockitem list
    if item:
        for i in item:
            response = hf.obj_to_dict(i)
            stockitem.append(response)
    
    # Display all the items on the page
    if request.method == 'GET':
        return render_template('stockid.html', stockitem=stockitem)

    return jsonify({"message": "No such stock ID"})


# route to display the items in the cart of the current user
@app.route("/cart", methods=['GET', 'POST'])
@hf.login_required
def cart():
    if 'cart' not in session:
        session['cart'] = []

    if request.method == 'GET':
        cartitem = session['cart']
        subtotal = 0
        for i in cartitem:
            subtotal += i.total
        return render_template('cart.html', caritem=cartitem, subtotal=subtotal)
    
    if request.method == 'POST':
       stockid = request.form.get('stockid')
       subtotal = 0
       if request.form.get('order') and int(request.form.get('order')) > 0:
          order = request.form.get('order')
          row = hf.obj_to_dict(Stock.query.get(stockid))
          id = row['id']
          description = row['description']
          price = row['price']
          total = row['price'] * float(order)
          cartitem = Cartitem(id=id, description=description, qty=order, price=price, total=total)
          session['cart'].append(cartitem)
          for i in session['cart']:
            subtotal += i.total
          return render_template('cart.html', cartitem=cartitem, subtotal=subtotal)
     
    return render_template('cart.html')

# Delete an item in the cart
@app.route("/delcartitem", methods=['POST'])
@hf.login_required
def remove():
    lineitem = request.form.get('lineitem')
    lineitem = int(lineitem)
    session['cart'].pop(lineitem)
    return redirect(url_for('cart'))

# Confirm the order and send mails to user and BulletScript to confirm
@app.route("/confirm", methods=['POST'])
@hf.login_required
def confirm():
    if 'cart' in session:
        # Mail to user for confirmation of order
        msg = Message('THANK YOU FOR YOUR ORDER!', sender='jjdttesting@gmail.com', recipients=[session['email']])
        msg.body = ('Your order has been received. We will be in touch soon!')
        mail.send(msg)

        # Mail to BS to inform them of the order
        subtotal = 0
        items = []
        for i in session['cart']:
            cartitem = hf.cartitem(i)
            items.append(cartitem)
            subtotal += i.total
            
        items.append(subtotal)
       

        msg = Message('NEW ORDER', sender='jjdttesting@gmail.com', recipients=['jjdttesting@gmail.com'], reply_to=session['email'])
        msg.body = (
            'You have received an order for ' +  session['name'] + '\n' + str(items)
        )
        mail.send(msg)

        session.pop('cart')
        return redirect(url_for('store'))