from flask import redirect, session
from functools import wraps
from datetime import datetime


# Some routes require the user to be logged in
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function


# Converts a YYYY-MM-DD date to words using datetime
def todate(date):
    try:
        format = datetime.strptime(date, "%Y-%m-%d")
        return format.strftime("%B %d, %Y")
    except:
        return date
