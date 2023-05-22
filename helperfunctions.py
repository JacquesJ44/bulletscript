from flask import redirect, render_template, request, session
from functools import wraps

# this function will translate an object from the STOCK class into JSON format
def obj_to_dict(self):
    return {
        "id": self.id,
        "description": self.description,
        "code": self.code,
        "count": self.count,
        "price": self.price
    }

# this function will translate an object from the Sub_email class into JSON format
def user_to_dict(self):
    return {
        "id": self.id,
        "email": self.email,
        "name": self.name,
        "password": self.password
    }
# this function will create a dictionary object of cart items in a session
def cartitem(self):
    return{
        "id": self.id,
        "description": self.description,
        "qty": self.qty,
        "price": self.price,
        "total": self.total
    }
# this function ensures that the user will be redirected to the login/signup page when the associated link is clicked
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("name") is None:
            return redirect("/signin")
        return f(*args, **kwargs)
    return decorated_function

# this function will display values with the 'R' prefix and 2 decimals
def zar(value):
#Format value as ZAR
    return f"R {value:,.2f}"