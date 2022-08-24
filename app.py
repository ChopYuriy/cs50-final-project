import os,  re

from flask import Flask, flash, redirect, render_template, request, session, url_for
from cs50 import SQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename  # Used to store filename
from helpers import login_required


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = SQL("sqlite:///final.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    return render_template("index.html")



@app.route("/index", methods=["GET", "POST"])
def home():
      if request.method == "GET":
       return redirect(url_for('index'))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return ("Must give username")

        if not password:
            return ("Must give password")

        if not confirmation:
            return ("Must give confirmation")

        if password != confirmation:
            return ("Password do not match")

        hash = generate_password_hash(password)
        
        try:
            new_user = db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        except:
            return ("Username already exists")

        session["user_id"] = new_user

        return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return ("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return ("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return ("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")    

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")           




@app.route("/addPhoto")
def uploader():
    path = 'static/uploads/'
    uploads = sorted(os.listdir(path), key=lambda x: os.path.getctime(path+x))        # Sorting as per image upload date and time
    print(uploads)
    
    uploads = ['uploads/' + file for file in uploads]
    uploads.reverse()
    # Pass filenames to front end for display in 'uploads' variable
    return render_template("addPhoto.html", uploads=uploads)


app.config['UPLOAD_PATH'] = 'static/uploads'             # Storage path


# This method is used to upload files
@app.route("/upload", methods=['GET', 'POST'])
def upload_file():                                       
    if request.method == 'POST':
        f = request.files['file']
        print(f.filename)
        
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        # Redirect to route 'addPhoto' for displaying images on front end
        return redirect("addPhoto")


if __name__ == "__main__":
    app.run()
