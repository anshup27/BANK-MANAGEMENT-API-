from flask import Flask, request, jsonify
import sqlite3
from flask_restful import Resource
from datetime import datetime
from dotenv import load_dotenv
import os 
load_dotenv()

import base64
username=os.getenv("USERNAME")
password=os.getenv("PASSWORD")
DB = "bank_new.db"



def require_auth():
    auth = request.headers.get('Authorization')
    
    if not auth:
        return True 

    try:
        scheme, encoded = auth.split()
        decoded = base64.b64decode(encoded).decode("utf-8")
        user, pwd = decoded.split(":")
    except:
        return jsonify({"error": "Invalid authentication format"}), 401

    if user ==username and pwd == password:
        return True
    else:
        return False 

    



def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    print("get_db")
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    print("Initializing DB...")

    # 1. Drop old tables (so schema changes apply)
    cur.execute("DROP TABLE IF EXISTS accounts")
    cur.execute("DROP TABLE IF EXISTS transactions")
    

    # 2. Create accounts table with status, phone, email, created_at
    cur.execute("""
    CREATE TABLE accounts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        balance REAL DEFAULT 0,
        status TEXT DEFAULT 'active',
        customer_phone TEXT,
        customer_email TEXT,
        created_at TEXT
    )
    """)

    # 3. Create transactions table
    cur.execute("""
    CREATE TABLE transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        type TEXT,
        amount REAL,
        ts TEXT,
        FOREIGN KEY(account_id) REFERENCES accounts(id)
    )
    """)

    conn.commit()

    # 4. Optional: insert demo accounts
    accounts = [
    ("Alice", 5000, "active", "1234567890", "alice@mail.com", datetime.now().isoformat()),
    ("Bob", 1500, "active", "9876543210", "bob@mail.com", datetime.now().isoformat())
    ]

    cur.executemany("""
    INSERT INTO accounts(
        name, balance, status, customer_phone, customer_email, created_at
    ) VALUES(?,?,?,?,?,?)
    """, accounts)


    conn.commit()

    # 5. Optional: insert demo transactions
    cur.execute("SELECT id, balance FROM accounts ORDER BY id")
    rows = cur.fetchall()
    id1 = rows[0]["id"]
    id2 = rows[1]["id"]

    transactions = [
        (id1, "deposit", 2000, datetime.now().isoformat()),
        (id2, "withdraw", 500, datetime.now().isoformat())
    ]
    cur.executemany(
        "INSERT INTO transactions(account_id, type, amount, ts) VALUES(?,?,?,?)",
        transactions
    )
    conn.commit()

    conn.close()
    print("✔ Database initialized with demo records.")



def to_dict(row):
    return dict(row) if row else None



class Accounts(Resource):
    def get(self):
        auth=require_auth()
        if not auth:
            return jsonify({"message":"user is not authorized"}),404
        print("get method ")
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM accounts")
        rows = cur.fetchall()
        print(rows)
        conn.close()
        return jsonify([to_dict(r) for r in rows])

    def post(self):
        auth=require_auth()
        if not auth:
            return jsonify({"message":"user is not authorized"}),404
        data = request.get_json() or {}
        name = data.get("name")
        balance = float(data.get("balance", 0))

        if not name:
            return {"error": "name is required"}, 400

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO accounts(name, balance) VALUES(?,?)", (name, balance))
        conn.commit()

        cur.execute("SELECT * FROM accounts WHERE id=?", (cur.lastrowid,))
        row = cur.fetchone()
        conn.close()

        return to_dict(row), 201



class Account(Resource):
    def get(self, id):
        auth=require_auth()
        if not auth:
            return jsonify({"message":"user is not authorized"}),404
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM accounts WHERE id=?", (id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return {"error": "not found"}, 404

        return to_dict(row)

    def put(self, id):
        auth=require_auth()
        if not auth:
            return jsonify({"message":"user is not authorized"}),404
        data = request.get_json() or {}
        name = data.get("name")
        balance = data.get("balance")

        conn = get_db()
        cur = conn.cursor()

        if name:
            cur.execute("UPDATE accounts SET name=? WHERE id=?", (name, id))

        if balance is not None:
            cur.execute("UPDATE accounts SET balance=? WHERE id=?", (float(balance), id))

        conn.commit()

        cur.execute("SELECT * FROM accounts WHERE id=?", (id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return {"error": "not found"}, 404

        return to_dict(row)

    def delete(self, id):
        auth=require_auth()
        if not auth:
            return jsonify({"message":"user is not authorized"}),404
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM accounts WHERE id=?", (id,))
        deleted = cur.rowcount

        cur.execute("DELETE FROM transactions WHERE account_id=?", (id,))
        conn.commit()
        conn.close()

        if deleted == 0:
            return {"error": "not found"}, 404

        return {"message": "deleted"}




class Deposit(Resource):
    def post(self):
        auth=require_auth()
        if not auth:
            return jsonify({"message":"user is not authorized"}),404
        data = request.get_json() or {}
        id = data.get("id")
        amt = float(data.get("amount", 0))

        conn = get_db()
        cur = conn.cursor()

        cur.execute("UPDATE accounts SET balance = balance + ? WHERE id=?", (amt, id))
        if cur.rowcount == 0:
            return {"error": "not found"}, 404

        cur.execute("""
            INSERT INTO transactions(account_id,type,amount,ts)
            VALUES(?,?,?,?)
        """, (id, "deposit", amt, datetime.now().isoformat()))

        conn.commit()

        cur.execute("SELECT * FROM accounts WHERE id=?", (id,))
        row = cur.fetchone()
        conn.close()

        return {"message": "deposit ok", "account": to_dict(row)}, 200



class Withdraw(Resource):
    def post(self):
        auth=require_auth()
        if not auth:
            return jsonify({"message":"user is not authorized"}),404
        data = request.get_json() or {}
        id = data.get("id")
        amt = float(data.get("amount", 0))

        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT balance FROM accounts WHERE id=?", (id,))
        row = cur.fetchone()

        if not row:
            return {"error": "not found"}, 404

        if row["balance"] < amt:
            return {"error": "insufficient funds"}, 400

        cur.execute("UPDATE accounts SET balance = balance - ? WHERE id=?", (amt, id))
        cur.execute("""
            INSERT INTO transactions(account_id,type,amount,ts)
            VALUES(?,?,?,?)
        """, (id, "withdraw", amt, datetime.now().isoformat()))

        conn.commit()

        cur.execute("SELECT * FROM accounts WHERE id=?", (id,))
        new = cur.fetchone()
        conn.close()

        return {"message": "withdraw ok", "account": to_dict(new)}, 200



class Transactions(Resource):
    def get(self, id):
        auth=require_auth()
        if not auth:
            return jsonify({"message":"user is not authorized"}),404
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM accounts WHERE id=?", (id,))
        row = cur.fetchone()

        if not row:
            return {"error": "not found"}, 404

        cur.execute("SELECT * FROM transactions WHERE account_id=?", (id,))
        rows = cur.fetchall()
        conn.close()

        return jsonify([to_dict(r) for r in rows])

class BlockAccount(Resource):
    def post(self):
        data = request.get_json()
        acc_id = data.get("id")

        conn = get_db()
        cur = conn.cursor()

        cur.execute("UPDATE accounts SET status='blocked' WHERE id=?", (acc_id,))
        conn.commit()

        if cur.rowcount == 0:
            return {"error": "Account not found"}, 404

        return {"message": "Account blocked"}, 200
    
class CloseAccount(Resource):
    def post(self):
        data = request.get_json()
        acc_id = data.get("id")

        conn = get_db()
        cur = conn.cursor()

        # Ensure zero balance
        cur.execute("SELECT balance FROM accounts WHERE id=?", (acc_id,))
        row = cur.fetchone()

        if not row:
            return {"error": "Account not found"}, 404
        
        if row["balance"] != 0:
            return {"error": "Balance must be zero to close account"}, 400

        cur.execute("UPDATE accounts SET status='closed' WHERE id=?", (acc_id,))
        conn.commit()

        return {"message": "Account closed"}, 200
class UpdateCustomer(Resource):
    def put(self, id):
        data = request.get_json()

        phone = data.get("phone")
        email = data.get("email")

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
        UPDATE accounts
        SET customer_phone=?, customer_email=?
        WHERE id=?
        """, (phone, email, id))

        conn.commit()

        if cur.rowcount == 0:
            return {"error": "Account not found"}, 404
        
        return {"message": "Customer info updated"}, 200
class ApplyInterest(Resource):
    def post(self):
        data = request.get_json()

        rate= data.get("rate")

        conn = get_db()
        cur = conn.cursor()

        # Only apply to active accounts
        cur.execute("""
        UPDATE accounts
        SET balance = balance + (balance * ?)
        WHERE status='active'
        """, (rate,))

        conn.commit()

        return {"message": "Interest applied"}, 200
class Statement(Resource):
    def get(self, id):
        output_format = request.args.get("format", "json")

        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM transactions WHERE account_id=?", (id,))
        tx = [dict(row) for row in cur.fetchall()]

        if output_format == "json":
            return jsonify(tx)

        return {"error": "Invalid format"}, 400

