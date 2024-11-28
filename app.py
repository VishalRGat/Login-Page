import streamlit as st
import sqlite3
from datetime import datetime
import hashlib

# Database Setup
conn = sqlite3.connect("users.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    middle_name TEXT,
    last_name TEXT,
    dob TEXT,
    age INTEGER,
    address_line1 TEXT,
    address_line2 TEXT,
    address_line3 TEXT,
    state TEXT,
    city TEXT,
    zip_code TEXT,
    email_id TEXT UNIQUE,
    password TEXT
)''')
conn.commit()

# Helper Functions
def calculate_age(dob):
    today = datetime.today()
    dob_date = datetime.strptime(dob, "%Y-%m-%d")
    return today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

# Pages
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def register_user():
    st.title("User Registration")
    
    with st.form("Registration Form"):
        first_name = st.text_input("First Name")
        middle_name = st.text_input("Middle Name")
        last_name = st.text_input("Last Name")
        dob = st.date_input("Date of Birth", max_value=datetime.today())
        address_line1 = st.text_input("Address Line 1")
        address_line2 = st.text_input("Address Line 2")
        address_line3 = st.text_input("Address Line 3")
        state = st.selectbox("State", ["Select State", "Maharashtra", "Karnataka", "Delhi", "Others"])
        city = st.text_input("City")
        zip_code = st.text_input("Zip Code")
        email_id = st.text_input("Email ID (used as User ID)")
        password = st.text_input("Set Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        submit = st.form_submit_button("Register")
        reset = st.form_submit_button("Reset")

        if submit:
            if not first_name or not last_name or not dob or state == "Select State" or not city or not email_id or not password:
                st.error("All fields are required!")
            elif password != confirm_password:
                st.error("Passwords do not match!")
            elif len(password) < 8 or not any(ch.isupper() for ch in password) or not any(ch.islower() for ch in password) or not any(ch.isdigit() for ch in password) or not any(ch in "!@#$%^&*()_+-=" for ch in password):
                st.error("Password must be at least 8 characters long, with an uppercase, lowercase, number, and special character.")
            else:
                age = calculate_age(str(dob))
                try:
                    c.execute('''INSERT INTO users (first_name, middle_name, last_name, dob, age, address_line1, address_line2, address_line3, state, city, zip_code, email_id, password)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                              (first_name, middle_name, last_name, dob, age, address_line1, address_line2, address_line3, state, city, zip_code, email_id, hash_password(password)))
                    conn.commit()
                    st.success("Registration successful! Please login.")
                except sqlite3.IntegrityError:
                    st.error("Email ID already exists!")

            if reset:
                st.experimental_rerun()

def login_user():
    st.title("Login")
    email_id = st.text_input("Email ID")
    password = st.text_input("Password", type="password")
    login = st.button("Login")
    
    if login:
        c.execute("SELECT password FROM users WHERE email_id = ?", (email_id,))
        record = c.fetchone()
        if record and verify_password(password, record[0]):
            st.session_state.logged_in = True
            st.session_state.user = email_id
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid email ID or password.")

def hello_world_page():
    st.title("Hello World")
    st.write(f"Welcome, {st.session_state.user}!")
    logout = st.button("Logout")
    if logout:
        st.session_state.logged_in = False
        st.experimental_rerun()

# Main App
if not st.session_state.logged_in:
    menu = st.sidebar.radio("Menu", ["Register", "Login"])
    if menu == "Register":
        register_user()
    elif menu == "Login":
        login_user()
else:
    hello_world_page()
