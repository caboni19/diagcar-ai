from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import fetch_one, execute


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        car_brand = request.form.get("car_brand", "").strip()
        car_model = request.form.get("car_model", "").strip()
        car_year = request.form.get("car_year", "").strip()
        fuel_type = request.form.get("fuel_type", "").strip()
        transmission = request.form.get("transmission", "").strip()
        mileage = request.form.get("mileage", "").strip()
        if not first_name or not email or not password:
            flash("Please fill required fields.", "error")
            return render_template("register.html")
        if fetch_one("SELECT id FROM users WHERE email=%s", (email,)):
            flash("This email already exists.", "error")
            return render_template("register.html")
        user_id = execute(
            """
            INSERT INTO users(
                first_name,last_name,email,phone,password_hash,
                car_brand,car_model,car_year,fuel_type,transmission,mileage
            ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                first_name, last_name, email, phone, generate_password_hash(password),
                car_brand, car_model, car_year or None, fuel_type, transmission, mileage or None
            ),
        )
        session["user"] = {
            "id": user_id, "first_name": first_name, "last_name": last_name, "email": email,
            "car_brand": car_brand, "car_model": car_model, "car_year": car_year,
            "fuel_type": fuel_type, "transmission": transmission, "mileage": mileage
        }
        return redirect(url_for("main.dashboard"))
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = fetch_one("SELECT * FROM users WHERE email=%s", (email,))
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")
        session["user"] = {
            "id": user["id"], "first_name": user["first_name"], "last_name": user["last_name"],
            "email": user["email"], "car_brand": user.get("car_brand"),
            "car_model": user.get("car_model"), "car_year": user.get("car_year"),
            "fuel_type": user.get("fuel_type"), "transmission": user.get("transmission"),
            "mileage": user.get("mileage")
        }
        return redirect(url_for("main.dashboard"))
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.home"))
