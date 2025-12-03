import json
from application import app
from application import init_db

client = app.test_client()

# ---------------------------------------------------
# Reset DB before each test
# ---------------------------------------------------
def setup_function(function):
    init_db()


# ---------------------------------------------------
# 1. Create Account
# ---------------------------------------------------
def test_create_account():
    res = client.post("/accounts", json={"name": "Alice", "balance": 200})
    assert res.status_code == 201
    data = res.get_json()
    assert data["name"] == "Alice"
    assert data["balance"] == 200


# ---------------------------------------------------
# 2. Get All Accounts
# ---------------------------------------------------
def test_get_all_accounts():
    client.post("/accounts", json={"name": "A"})
    client.post("/accounts", json={"name": "B"})

    res = client.get("/accounts")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)
   


# ---------------------------------------------------
# 3. Get Account By ID
# ---------------------------------------------------
def test_get_account_by_id():
    res = client.post("/accounts", json={"name": "Test"})
    acc = res.get_json()
    acc_id = acc["id"]

    res = client.get(f"/accounts/{acc_id}")
    assert res.status_code == 200
    assert res.get_json()["name"] == "Test"


# ---------------------------------------------------
# 4. Update Account
# ---------------------------------------------------
def test_update_account():
    res = client.post("/accounts", json={"name": "Bob", "balance": 500})
    acc = res.get_json()
    acc_id = acc["id"]

    res = client.put(f"/accounts/{acc_id}", json={"name": "Bobby", "balance": 600})
    assert res.status_code == 200

    data = res.get_json()
    assert data["name"] == "Bobby"
    assert data["balance"] == 600


# ---------------------------------------------------
# 5. Deposit Money
# ---------------------------------------------------
def test_deposit():
    res = client.post("/accounts", json={"name": "Sam"})
    acc = res.get_json()
    acc_id = acc["id"]

    res = client.post("/accounts/deposit", json={"id": acc_id, "amount": 100})
    assert res.status_code == 200

    data = res.get_json()
    assert data["account"]["balance"] == 100


# ---------------------------------------------------
# 6. Withdraw Success
# ---------------------------------------------------
def test_withdraw_success():
    res = client.post("/accounts", json={"name": "Tom", "balance": 200})
    acc = res.get_json()
    acc_id = acc["id"]

    res = client.post("/accounts/withdraw", json={"id": acc_id, "amount": 50})
    assert res.status_code == 200

    data = res.get_json()
    assert data["account"]["balance"] == 150


# ---------------------------------------------------
# 7. Withdraw Fail
# ---------------------------------------------------
def test_withdraw_fail():
    res = client.post("/accounts", json={"name": "Mark", "balance": 20})
    acc = res.get_json()
    acc_id = acc["id"]

    res = client.post("/accounts/withdraw", json={"id": acc_id, "amount": 100})
    assert res.status_code == 400
    assert res.get_json()["error"] == "insufficient funds"


# ---------------------------------------------------
# 8. Transaction History
# ---------------------------------------------------
def test_transaction_history():
    res = client.post("/accounts", json={"name": "Alex", "balance": 100})
    acc = res.get_json()
    acc_id = acc["id"]

    client.post("/accounts/deposit", json={"id": acc_id, "amount": 50})
    client.post("/accounts/withdraw", json={"id": acc_id, "amount": 30})

    res = client.get(f"/accounts/{acc_id}/transactions")
    assert res.status_code == 200

    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) == 2


# ---------------------------------------------------
# 9. Delete Account
# ---------------------------------------------------
def test_delete_account():
    res = client.post("/accounts", json={"name": "Test"})
    acc = res.get_json()
    acc_id = acc["id"]

    res = client.delete(f"/accounts/{acc_id}")
    assert res.status_code == 200
    assert res.get_json()["message"] == "deleted"
