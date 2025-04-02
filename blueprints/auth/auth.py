from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import pyodbc
from werkzeug.security import generate_password_hash, check_password_hash
from sql.db_connection import connection_string
from flask_dance.contrib.google import make_google_blueprint, google
from functools import wraps
import uuid
import os
from translations import translations
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

# Create the main auth blueprint
auth_bp = Blueprint('auth', __name__)

# Create the Flask-Dance Google blueprint
google_bp = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_url="/auth/login/google/authorized"  # URL to redirect after Google auth
)

# -------------------------------
# Normal Registration Endpoint
# -------------------------------
@auth_bp.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username   = request.form.get('username')
        password   = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name  = request.form.get('last_name')
        
        # Hash the password
        password_hash = generate_password_hash(password)
        try:
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            insert_query = """
                INSERT INTO Users (username, password, first_name, last_name)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(insert_query, (username, password_hash, first_name, last_name))
            conn.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('auth.login'))
        except pyodbc.Error as e:
            print(f"Error inserting user: {e}")
            flash("An error occurred during registration.", "error")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
            lang = request.args.get('lang', session.get('lang', 'no'))
            session['lang'] = lang
    return render_template('register_user.html', t=translations.get(lang, translations['no']), lang=lang)

# -------------------------------
# Normal Login Endpoint
# -------------------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Ensure `lang` is always defined
    lang = request.args.get('lang', session.get('lang', 'no'))
    session['lang'] = lang
    if request.method == 'POST':
        identifier = request.form.get('identifier')  # can be username or email
        password = request.form.get('password')
        try:
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            query = """
                SELECT id, username, email, password, active FROM Users
                WHERE username = ? OR email = ?
            """
            cursor.execute(query, (identifier, identifier))
            row = cursor.fetchone()
            if row:
                user_id, username, email, stored_password, active = row
                if active and check_password_hash(stored_password, password):
                    session['user_id'] = user_id
                    flash("Login successful!", "success")
                    return redirect(url_for('admin_page', lang=lang))
                else:
                    flash("Invalid credentials or inactive account.", "error")
            else:
                flash("User not found.", "error")
        except pyodbc.Error as e:
            print(f"Login error: {e}")
            flash("An error occurred during login.", "error")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    return render_template('login.html', t=translations.get(lang, translations['no']), lang=lang)

# -------------------------------
# Logout Endpoint
# -------------------------------
@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('index'))

# -------------------------------
# Google Login Endpoint
# -------------------------------
@auth_bp.route('/login/google')
def google_login():
    # If not already authorized with Google, redirect to the Flask-Dance login route
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    # Once authorized, fetch user info from Google
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.", "error")
        return redirect(url_for("auth.login"))
    
    user_info = resp.json()
    email = user_info.get("email")
    username = email.split("@")[0]  # derive username from email

    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        # Check if a user with this email exists
        query = "SELECT id FROM Users WHERE email = ?"
        cursor.execute(query, (email,))
        row = cursor.fetchone()
        if row:
            user_id = row[0]
        else:
            # Create new user using a random password (not used since Google handles auth)
            random_password = uuid.uuid4().hex
            password_hash = generate_password_hash(random_password)
            insert_query = """
                INSERT INTO Users (username, email, password, active)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(insert_query, (username, email, password_hash, 1))
            conn.commit()
            # Retrieve the new user's ID using SQL Server's @@IDENTITY (or SCOPE_IDENTITY() if needed)
            cursor.execute("SELECT @@IDENTITY")
            new_row = cursor.fetchone()
            user_id = new_row[0] if new_row and new_row[0] else None
            if user_id is None:
                flash("Failed to create user from Google login.", "error")
                return redirect(url_for("auth.login"))
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error during Google login: {e}")
        flash("A database error occurred during Google login.", "error")
        return redirect(url_for("auth.login"))
    
    # Store the user id in session to mark the user as logged in
    session["user_id"] = user_id
    flash("Logged in with Google successfully!", "success")
    return redirect(url_for("index"))

@auth_bp.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    # Ensure `lang` is always defined
    lang = request.args.get('lang', session.get('lang', 'no'))
    session['lang'] = lang

    if request.method == 'POST':
        username   = request.form.get('username')
        email      = request.form.get('email')
        password   = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name  = request.form.get('last_name')
        # Optional: Get the active status (if you have a checkbox, for example)
        active     = request.form.get('active', 1)

        # Hash the password
        password_hash = generate_password_hash(password)
        try:
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            insert_query = """
                INSERT INTO Users (username, email, password, first_name, last_name, active)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (username, email, password_hash, first_name, last_name, active))
            conn.commit()
            flash("New user created successfully!", "success")
            # Redirect to the same page or elsewhere as desired.
            return redirect(url_for('auth.create_user', lang=lang))
        except pyodbc.Error as e:
            print(f"Error creating user: {e}")
            flash("An error occurred while creating the user.", "error")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    return render_template('create_user.html', t=translations.get(lang, translations['no']), lang=lang)