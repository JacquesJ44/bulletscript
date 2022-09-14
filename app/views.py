from app import app

from flask import render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime

#Creating an instance of the SQLAlchemy module to create a class fal
db = SQLAlchemy(app)

#Creating a class sub_email - this is the table of the db
class sub_email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30))
    date_joined = db.Column(db.DateTime)

# Create an instance of the Mail class
mail = Mail(app)

print(app.config)

#Display '/' route with GET; save email to database and forward welcome mail on POST
@app.route("/", methods=["GET", "POST"])
def getform():
    #If the user reaches this route via GET then display the webpage
    if request.method == "GET":
        return render_template('index.html')

    if request.method == "POST":
        #If text box is empty when submit button is hit
        if not request.form['email']:
            flash("Please enter valid email address", "error")
        else:
            email = request.form['email']
            #If email address already exists in the database
            if sub_email.query.filter_by(email=email).all():
                flash("You are already subscribed", "info")
            else:
                #Add email address to database if it doesn't exist yet
                newEmail = sub_email(email=email, date_joined=datetime.now())

                db.session.add(newEmail)
                db.session.commit()

                flash("Thank you for subscribing", "info")

                # Mail the contact form information
                msg = Message('Welcome', sender='jjdttesting@gmail.com', recipients=[email], reply_to='jjdttesting@gmail.com')
                msg.body = ('Thank you for subscribing.')
                mail.send(msg)

        return render_template('index.html')

#Creating the STORE route
@app.route("/store")
def store():
    return render_template('store.html')