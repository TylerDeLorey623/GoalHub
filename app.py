import sqlite3
import random

from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, todate
from datetime import datetime


# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["todate"] = todate

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to a database
conn = sqlite3.connect("goalhub.db", check_same_thread=False)

# Set the row_factory to sqlite3.Row to enable dictionary-like access
conn.row_factory = sqlite3.Row

db = conn.cursor()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    # Get username for nice index display (if logged in)
    name = ''
    if session.get("user_id") is not None:
        logged = True
        rows = db.execute("SELECT username FROM users WHERE id = ?",
                          [session["user_id"]]).fetchone()
        text = "Logged in as"
        name = rows['username']
    else:
        logged = False
        text = "You are currently browsing as guest. Login to gain access to all features!"

    return render_template("index.html", text=text, name=name, logged=logged)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    file = "register.html"

    # Forget any user_id
    session.clear()

    # Register user if they submit form
    if request.method == "POST":

        # Get user input
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return render_template(file, alert="Must provide username!")

        # Ensure password was submitted
        elif not password:
            return render_template(file, alert="Must provide password!")

        # Ensure confirmation was submitted
        elif not confirmation:
            return render_template(file, alert="Must provide confirmation!")

        # Ensure username doesn't already exist
        elif db.execute("SELECT * FROM users WHERE username = ?", [username]).fetchone():
            return render_template(file, alert="Username already exists!")

        # Ensure password matches confirmation
        elif password != confirmation:
            return render_template(file, alert="Password does not match confirmation!")

        # Create new user in database if it is valid
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)", [username, generate_password_hash(
                password)]
        )

        # Commit insertion
        conn.commit()

        # Query database for the new user
        rows = db.execute("SELECT * FROM users WHERE username = ?", [username]).fetchone()

        # Remember which user has logged in
        session["user_id"] = rows["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template(file)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    file = "login.html"

    # Forget any user_id
    session.clear()

    # User reached route via POST by submitting form
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return render_template(file, alert="Must provide username!")
        elif not password:
            return render_template(file, alert="Must provide password!")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", [username]).fetchone()

        # Ensure username exists and password is correct
        if not rows or not check_password_hash(rows["password_hash"], password):
            return render_template(file, alert="Invalid username and/or password!")

        # Remember which user has logged in
        session["user_id"] = rows["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET by clicking link or redirect
    else:
        return render_template(file)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/changePassword", methods=["GET", "POST"])
@login_required
def changePassword():
    """Change user password"""

    file = "changePassword.html"

    # Change password if they submit form
    if request.method == "POST":

        # Get user input
        original = request.form.get("original")
        new = request.form.get("new")
        confirmation = request.form.get("confirmation")

        # Ensure original was submitted
        if not original:
            return render_template(file, alert="Must provide original password!")

        # Ensure new password was submitted
        elif not new:
            return render_template(file, alert="Must provide new password!")

        # Ensure confirmation was submitted
        elif not confirmation:
            return render_template(file, alert="Must provide confirmation!")

        # Ensure password matches old password
        oldHashedPassword = db.execute("SELECT password_hash FROM users WHERE id = ?", [
                                       session["user_id"]]).fetchone()
        if not check_password_hash(oldHashedPassword["password_hash"], original):
            return render_template(file, alert="Original password does not match!")

        # Ensure new password matches confirmation
        elif new != confirmation:
            return render_template(file, alert="New password does not match confirmation!")

        # Update users table with new password
        db.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                   [generate_password_hash(new), session["user_id"]])

        # Commit changes
        conn.commit()

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template(file)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create new goals"""

    file = "create.html"

    # Create the goal if valid form was submitted
    if request.method == "POST":
        priority = request.form.get("priority")
        goal = request.form.get("goal")
        date = request.form.get("date")

        # Ensure everything was submitted
        if not priority:
            return render_template(file, alert="Must provide priority!")
        elif not goal:
            return render_template(file, alert="Must provide goal!")
        elif not date:
            return render_template(file, alert="Must provide date!")

        # Check if date submitted is before today's date
        today = datetime.today().date()

        date = datetime.strptime(date, "%Y-%m-%d").date()

        if date < today:
            return render_template(file, alert="The date cannot be in the past!")

        # Add goal to goals table
        db.execute("INSERT INTO goals (user_id, priority, goal, goal_date) VALUES (?, ?, ?, ?)", [
                   session["user_id"], priority, goal, date])

        # Commit insertion
        conn.commit()

        # Redirect to progress page
        return redirect("/progress")

    # User reached route via GET by clicking link or redirect
    else:
        return render_template(file)


@app.route("/progress", methods=["GET", "POST"])
@login_required
def progress():
    """ Shows all existing goals """

    # Default sorting values
    orderby = "timestamp DESC"

    # Sorting method for the progress table
    if request.method == "POST":
        sort = request.form.get("sort")
        order = request.form.get("order")
        if sort and order:
            if sort == "Priority":
                orderby = "CASE priority WHEN 'Very High' THEN 5 WHEN 'High' THEN 4 WHEN 'Medium' THEN 3 WHEN 'Low' THEN 2 WHEN 'Very Low' THEN 1 ELSE 0 END "
            elif sort == "Goal Completion Date":
                orderby = "goal_date"
            elif sort == "Date Submitted":
                orderby = "timestamp"

            if order == "Ascending":
                orderby += " ASC"
            else:
                orderby += " DESC"

    # Get the user's goals
    goals = db.execute(f"SELECT priority, goal, goal_date, timestamp FROM goals WHERE user_id = ? ORDER BY {orderby}", [
                       session["user_id"]]).fetchall()

    # Get username
    user = db.execute("SELECT username FROM users WHERE id = ?", [session["user_id"]]).fetchone()

    return render_template("progress.html", goals=goals, user=user["username"])


@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    """Remove goals"""

    file = "remove.html"

    # Get user's goals
    goals = db.execute("SELECT goal FROM goals WHERE user_id = ? ORDER BY timestamp DESC", [
                       session["user_id"]]).fetchall()

    # Remove certain goal if user submitted valid form
    if request.method == "POST":
        # Get information from form
        selectedGoal = request.form.get("selectedGoal")

        # Validate user input
        if not selectedGoal:
            return render_template(file, alert="Must provide goal to remove!", goals=goals)

        # Removed the selected goal
        db.execute("DELETE FROM goals WHERE user_id = ? AND goal = ?",
                   [session["user_id"], selectedGoal])

        # Commit insertion
        conn.commit()

        # Redirect to progress page
        return redirect("/progress")

    # User reached route via GET by clicking link or redirect
    else:
        return render_template(file, goals=goals)


@app.route("/motivation")
@login_required
def motivation():
    # List of motivational videos that could be chosen
    videos = [
        "https://www.youtube.com/embed/QbL0X3B4mjg?si=SL5ugIwKurbR9EK5",
        "https://www.youtube.com/embed/ZTHy7KhudkM?si=dYindQ5bfMx1HBuq",
        "https://www.youtube.com/embed/GWVPcjMBuAg?si=fCY7Reeyb3FFm25i",
        "https://www.youtube.com/embed/jB2nWAAuXpA?si=suDsqOQII97U1CIn",
        "https://www.youtube.com/embed/1bumPyvzCyo?si=XeAJOOZuRqXGjnFg",
        "https://www.youtube.com/embed/DoA-a-g2o4g?si=cryEaRq69Jiq34gF",
        "https://www.youtube.com/embed/tbnzAVRZ9Xc?si=xr7RhcAgI8ZperTN",
        "https://www.youtube.com/embed/ZXsQAXx_ao0?si=HiSN2Gr4MgK9ZcOI"
    ]

    # Chose a video at random to display on the page
    video = random.choice(videos)

    return render_template("motivation.html", video=video)
