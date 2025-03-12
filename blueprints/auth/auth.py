from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import pyodbc
from werkzeug.security import generate_password_hash, check_password_hash
from sql.db_connection import connection_string

auth_bp = Blueprint('auth', __name__)

# Registration endpoint
@auth_bp.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Hash the password
        password_hash = generate_password_hash(password)

        try:
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            insert_query = """
                INSERT INTO Users (username, password, first_name, last_name)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (username, password_hash, first_name, last_name))
            conn.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('auth.login'))
        except pyodbc.Error as e:
            print(f"Error inserting user: {e}")
            flash("An error occurred during registration.", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    return render_template('register_user.html')

# Login endpoint
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')  # can be username or email
        password = request.form.get('password')
        try:
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            # Look for a user with the given username or email
            query = """
                SELECT id, username, email, password, active FROM Users
                WHERE username = ?
            """
            cursor.execute(query, (identifier, identifier))
            row = cursor.fetchone()
            if row:
                user_id, username, stored_password, active = row
                if active and check_password_hash(stored_password, password):
                    # Successful login, store the user id in the session
                    session['user_id'] = user_id
                    flash("Login successful!", "success")
                    return redirect(url_for('index'))
                else:
                    flash("Invalid credentials or inactive account.", "error")
            else:
                flash("User not found.", "error")
        except pyodbc.Error as e:
            print(f"Login error: {e}")
            flash("An error occurred during login.", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template('admin_status.html')

# Logout endpoint
@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('index'))
