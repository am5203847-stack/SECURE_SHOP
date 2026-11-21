from flask import send_file
from flask import Flask, request, session, jsonify
from markupsafe import escape
import sqlite3, hashlib, os
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['DEBUG'] = False
def hash_pass(p):
    return hashlib.pbkdf2_hmac('sha256', p.encode(), b'salt_pharaoh', 100000).hex()
def get_db():
    db = sqlite3.connect('shop.db')
    db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT, pass TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER)")
    db.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user_id INTEGER, product_id INTEGER)")
    if db.execute("SELECT COUNT(*) FROM products").fetchone()[0]==0:
        db.execute("INSERT INTO products (name, price) VALUES ('T-Shirt', 350)")
        db.execute("INSERT INTO products (name, price) VALUES ('Shoes', 900)")
        db.execute("INSERT INTO products (name, price) VALUES ('Cap', 200)")
    db.commit()
    return db
@app.route('/register', methods=['POST'])
def register():
    email = request.json.get('email','')
    password = request.json.get('password','')
    if '@' not in email or len(password) < 8:
        return jsonify({'error':'bad'}), 400
    db = get_db()
    try:
        db.execute("INSERT INTO users (email, pass) VALUES (?, ?)", (email, hash_pass(password)))
        db.commit()
    except:
        return jsonify({'error':'exists'}), 400
    return jsonify({'ok':'done'})
@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email','')
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not user or user[2] != hash_pass(request.json.get('password','')):
        return jsonify({'error':'wrong'}), 401
    session['user_id']=user[0]
    return jsonify({'ok':'logged'})
@app.route('/')
def home():
    return send_file('index.html')

@app.route('/products')
def products():
    db = get_db()
    rows = db.execute("SELECT id, name, price FROM products").fetchall()
    data = [{'id':r[0], 'name':str(escape(r[1])), 'price':r[2]} for r in rows]
    return jsonify(data)
@app.route('/order', methods=['POST'])
def order():
    if 'user_id' not in session:
        return jsonify({'error':'login first'}), 401
    pid = request.json.get('product_id')
    if not isinstance(pid, int):
        return jsonify({'error':'bad id'}), 400
    db = get_db()
    prod = db.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    if not prod:
        return jsonify({'error':'not found'}), 404
    db.execute("INSERT INTO orders (user_id, product_id) VALUES (?, ?)", (session['user_id'], pid))
    db.commit()
    return jsonify({'ok':'ordered', 'product':str(escape(prod[1]))})
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return {'ok':'logged out'}

@app.route('/myorders')
def myorders():
    if 'user_id' not in session:
        return jsonify({'error':'login first'}), 401
    db = get_db()
    rows = db.execute("SELECT products.name FROM orders JOIN products ON orders.product_id=products.id WHERE orders.user_id=?", (session['user_id'],)).fetchall()
    return jsonify([str(escape(r[0])) for r in rows])
if __name__=='__main__':
    app.run(host='127.0.0.1', port=5000)
