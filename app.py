from flask import Flask, render_template, redirect, request, session, url_for, flash, get_flashed_messages
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SECRET_KEY'] = 'app.secret_key'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Define a route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu.html',methods=['POST'])
def record_submission():
    if (request.method == "POST"):
        name = request.form['name']
        room = request.form['room']
        phone = request.form['phone']
        price = request.form['total_price']

        conn = sqlite3.connect('orders.db')
        curr = conn.cursor()

        # Create the customers table if it does not exist
        curr.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                phone_number TEXT,
                name TEXT,
                price INTEGER,
                address TEXT
            )
        ''')

        # Insert the data into the customers table
        curr.execute('''
            INSERT INTO customers (phone_number, name, price, address)
            VALUES (?, ?, ?, ?)
        ''', (phone, name, price, room))

        conn.commit()
        conn.close()

        return redirect('/orders.html')

@app.route('/orders.html')
def display_orders():
    conn = sqlite3.connect('orders.db')
    curr = conn.cursor()
    # Create the customers table if it does not exist
    curr.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            phone_number TEXT,
            name TEXT,
            price INTEGER,
            address TEXT
        )
    ''')


    curr.execute('SELECT rowid, * FROM customers')
    customers = curr.fetchall()
    conn.close()

    return render_template('orders.html', customers=customers)



@app.route('/index.html')
def index2():
    return render_template('index.html')

    
def get_menu_items():
    conn = sqlite3.connect('menu_items.db')
    cursor = conn.cursor()

    
    # Create table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS menu_items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  item_name TEXT NOT NULL,
                  item_class TEXT NOT NULL,
                  base_price INTEGER NOT NULL,
                  description TEXT NOT NULL,
                  image_path TEXT)''')
    conn.commit()

    cursor.execute("SELECT item_name, base_price, description, image_path FROM menu_items")
    menu_items = cursor.fetchall()

    conn.close()

    return menu_items

@app.route('/menu.html')
def menu():
    menu_items = get_menu_items()
    return render_template('menu.html', menu_items=menu_items)

@app.route('/orders.html')
def orders():
    return render_template('orders.html')

@app.route('/cook.html')
def cook():
    return render_template('cook.html')

@app.route('/private.html')
def private():
    return render_template('private.html')


def get_db():
    conn = sqlite3.connect('cooks.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS logins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL)''')
    return conn

@app.route('/cook.html', methods=['GET', 'POST'])
def sign():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'signin':
            username1 = request.form.get('username1')
            password1 = request.form.get('password1')
            conn = get_db()
            cur = conn.cursor()
            cur.execute('SELECT * FROM logins WHERE username = ? AND password = ?', (username1, password1))
            user = cur.fetchone()
            if user:
                session['user'] = user[1]
                return redirect(url_for('private'))
            else:
                flash('Invalid username or password.','error')
                return redirect(url_for('cook'))
        elif action == 'signup':
            username2 = request.form.get('username2')
            password2 = request.form.get('password2')
            conn = get_db()
            cur = conn.cursor()
            cur.execute('INSERT INTO logins (username, password) VALUES (?, ?)', (username2, password2))
            conn.commit()
            session['user'] = username2
            return redirect(url_for('private'))
    else:
        # render the sign-in/sign-up form
        return render_template('cook.html')




@app.route('/private.html', methods=['POST'])
def new_menu_item():

    # Set up database connection
    conn = sqlite3.connect('menu_items.db')
    c = conn.cursor()
    
    # Create table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS menu_items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  item_name TEXT NOT NULL,
                  item_class TEXT NOT NULL,
                  base_price INTEGER NOT NULL,
                  description TEXT NOT NULL,
                  image_path TEXT)''')
    conn.commit()

    # Get form data
    item_name = request.form['item-name']
    item_class = request.form['item-class']
    base_price = request.form['base-price']
    description = request.form['description']
    
    # Save image file and get path
    image_file = request.files['image']
    if image_file:
        filename = image_file.filename
        image_path = 'static/images/' + filename
        image_file.save(image_path)
    else:
        image_path = None
    
    # Save data to database
    c.execute('''INSERT INTO menu_items
                 (item_name, item_class, base_price, description, image_path)
                 VALUES (?, ?, ?, ?, ?)''',
              (item_name, item_class, base_price, description, image_path))
    conn.commit()
    
    return redirect(url_for('menu'))

if __name__ == '__main__':
    app.run(debug=True)