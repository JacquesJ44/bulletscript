from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
from decouple import config

#Create an instance of the Flask app
app = Flask(__name__)

#Configuring the Flask application
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = config('DATABASE_URL')
app.config['SECRET_KEY'] = config('SECRET_KEY')

#Creating an instance of the SQLAlchemy module to create a class 
db = SQLAlchemy(app)

#Creating a class sub_email - this is the table of the db
class sub_email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30))
    date_joined = db.Column(db.DateTime)

# Configure email server parameters
# app.config['MAIL_DEFAULT_SENDER']=config('EMAIL_DEFAULT_SENDER')
app.config['MAIL_SERVER']=config('EMAIL_HOST')
app.config['MAIL_PORT']=config('EMAIL_PORT')
app.config['MAIL_USERNAME']=config('EMAIL_HOST_USER')
app.config['MAIL_PASSWORD']=config('EMAIL_HOST_PASSWORD')
# app.config['MAIL_USE_TLS']=config('EMAIL_USE_TLS')
app.config['MAIL_USE_SSL']=config('EMAIL_USE_SSL')

# Create an instance of the Mail class
mail = Mail(app)

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


if __name__ == "__main__":
    app.run(config('DEBUG'))