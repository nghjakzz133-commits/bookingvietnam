from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User, Booking
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("index.html")

# =========================
# REGISTER
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"))

        if User.query.filter_by(email=email).first():
            flash("Email đã tồn tại")
            return redirect(url_for("register"))

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Đăng ký thành công!")
        return redirect(url_for("login"))

    return render_template("register.html")

# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Sai email hoặc mật khẩu")

    return render_template("login.html")

# =========================
# LOGOUT
# =========================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
@login_required
def dashboard():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", bookings=bookings)

# =========================
# CREATE BOOKING
# =========================
@app.route("/book", methods=["POST"])
@login_required
def book():
    venue = request.form.get("venue")
    date = request.form.get("date")
    time = request.form.get("time")
    guests = request.form.get("guests")

    new_booking = Booking(
        venue_name=venue,
        date=date,
        time=time,
        guest_count=int(guests),
        user_id=current_user.id
    )

    db.session.add(new_booking)
    db.session.commit()

    return redirect(url_for("dashboard"))

# =========================
# CREATE DATABASE
# =========================
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
