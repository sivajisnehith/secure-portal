from flask import Flask, render_template, request,redirect,url_for,session
from db import get_db
from cryptography.fernet import Fernet
import os
import time
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
app.secret_key = "fa562cf346ffa8cb8faba7491e0da04ea9011e7f7aad1c5b8179099111e6d077"
@app.route("/")
def home():
    return "Server running"
SESSION_TIMEOUT = 20
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email,password)
        )

        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            session["user"] = email
            session["expires_at"] = time.time()+SESSION_TIMEOUT
            return redirect(url_for("vitopia"))
        else:
            #login failed
            return render_template(
                "login.html",
                message = "Invalid email or password"
            )
        return f"You entered: {email} / {password}"


@app.route("/vitopia")
def vitopia():
    if "user" not in session:
        return render_template("login.html")
    
    if time.time()>session.get("expires_at",0):
        session.clear()
        return render_template("login.html")
    
    return render_template("vitopia.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT id FROM users WHERE email = %s",(email,))
        user = cursor.fetchone()

        if user:
            cursor.close()
            db.close()
            return render_template(
                "register.html",
                message = "Email already exists"
            )
        
        cursor.execute(
            "INSERT INTO users (email,password) VALUES (%s , %s)",
            (email,password)
        )
        db.commit()
        cursor.close()
        db.close()

        return render_template(
                "register.html",
                message = "Account create successfully"
            )
    
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

fernet = Fernet(os.getenv("FERNET_KEY"))
RESET_TOKEN_TTL = 10

@app.route("/forgot",methods=["GET","POST"])
def forgot():
    if request.method == "GET":
        return render_template("forgot.html")
    
    email = request.form.get("email")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if not user:
        return render_template(
            "forgot.html",
            message="Email not found"
        )
    
    token = fernet.encrypt(email.encode()).decode()

    reset_link = f"http://127.0.0.1:5000/reset/{token}"

    return redirect(url_for("forgot_success",token = token))
    

@app.route("/reset/<token>",methods = ["GET","POST"])
def reset(token):
    try:
        email = fernet.decrypt(
        token.encode(),
        ttl=RESET_TOKEN_TTL
        ).decode()
    except:
        return "Invalid or expired token"
    
    if request.method == "GET":
        return render_template("reset.html")
    
    new_password = request.form.get("password")

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
         "UPDATE users SET password=%s WHERE email=%s",
        (new_password, email)
    )
    db.commit()
    cursor.close()
    db.close()

    return "password reset successful. <a href ='/login'>login</a>"

@app.route("/forgot/success/<token>")
def forgot_success(token):
    reset_link = f"http://127.0.0.1:5000/reset/{token}"
    return render_template(
        "resetlink.html",
        message="Reset link generated",
        link=reset_link
    )
if __name__ == "__main__":
    app.run(debug=True)
