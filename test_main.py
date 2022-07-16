from fastapi import FastAPI
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

fake_db = ('1XPWD40X1ED215307 ', ' 1XKWDB0X57J211825', '1XP5DB9X7YN526158', '4V4NC9EJXEN171694', '1XP5DB9X7XD487964',
           '1XP5DB9X7XD487964')

no_matching_vin = ('11111111111111111', 'AAAAAAAAAAAAAAAAA','1XP5DB9X7XD48796444','11P5DB9X7XD487964', 'XP5DB9X7XD487964',
           '11P5DB9X7XD487964')

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Welcome to VIN Decoding!"}


def test_call_VPIC_API_Insert_into_db():
    response = client.get('/lookup/11111111111111111')
    assert response.status_code == 400
    assert response.json() == {"detail": "Failed to check the database for records because of the error"}

