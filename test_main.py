from fastapi import FastAPI
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Welcome to VIN Decoding!"}


def test_call_VPIC_API_Insert_into_db_errors1():
    response = client.get('/lookup/11111111111111111 ')
    assert response.status_code == 400
    assert response.json() == {"detail": "There was no response or an error returned by the API"}

def test_call_VPIC_API_Insert_into_db_errors2():
    response = client.get('/lookup/111111111111111111')
    assert response.status_code == 400
    assert response.json() == {"detail": "It should contain exactly 17 alphanumeric characters."}

def test_call_VPIC_API_Insert_into_db_errors3():
    response = client.get('/lookup/1XP5DB!X7X_487964')
    assert response.status_code == 400
    assert response.json() == {"detail": "It should contain exactly 17 alphanumeric characters."}


def test_call_VPIC_API_Insert_into_db1():
    response = client.get('/lookup/ 1XPWD40X1ED215307')
    assert response.status_code == 201
    assert response.json() == {"VIN"           : "1XPWD40X1ED215307",
                               "Make"          : "PETERBILT",
                               "Model"         : "388",
                               "Model Year"    : "2014",
                               "Body Class"    : "Truck-Tractor",
                               "Cached Results": False}

def test_call_VPIC_API_Insert_into_db2():
    response = client.get('/lookup/1XPWD40X1ED215307 ')
    assert response.status_code == 200
    assert response.json() == {"VIN"           : "1XPWD40X1ED215307",
                               "Make"          : "PETERBILT",
                               "Model"         : "388",
                               "Model Year"    : "2014",
                               "Body Class"    : "Truck-Tractor",
                               "Cached Results": True}


def test_delete1():
    response = client.get('/remove/1XPWD40X1ED215307')
    assert response.status_code == 200
    assert response.json() == {
        "Cached Deleted": True
    }

def test_delete2():
    response = client.get('/remove/1XPWD40X1ED215307')
    assert response.status_code == 200
    assert response.json() == {
        "Cached Deleted": False
    }


def test_delete_errors():
    response = client.get('/remove/1XPWD40X1ED21530@')
    assert response.status_code == 400
    assert response.json() == {
        "detail": "It should contain exactly 17 alphanumeric characters."
    }


def test_export():
    response = client.get('/export')
    assert response.status_code == 200
