import pytest
from app import app, fetch_currency_data, currency_updater, current_rates
import json
import requests_mock
from unittest.mock import patch

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_fetch_currency_data(requests_mock):
     mock_data = {
        "Date": "2023-10-26T11:30:00+03:00",
        "PreviousDate": "2023-10-25T11:30:00+03:00",
        "PreviousURL": "//www.cbr-xml-daily.ru/archive/2023/10/25/daily_json.js",
        "Timestamp": "2023-10-26T12:00:00+03:00",
        "Valute": {
            "USD": {
              "ID": "R01235",
              "NumCode": "840",
              "CharCode": "USD",
              "Nominal": 1,
              "Name": "Доллар США",
              "Value": 93.5142,
              "Previous": 93.6616
             },
           "EUR": {
              "ID": "R01239",
              "NumCode": "978",
              "CharCode": "EUR",
              "Nominal": 1,
              "Name": "Евро",
              "Value": 99.2089,
              "Previous": 99.4007
            }
         }
    }
     requests_mock.get('https://www.cbr-xml-daily.ru/daily_json.js', json=mock_data)
     data = fetch_currency_data()
     assert data == mock_data['Valute']


def test_currency_updater():
    with patch('app.fetch_currency_data', return_value={'USD': {'Value': 100, 'Previous': 90}, 'EUR': {'Value': 110, 'Previous': 100}}):
        currency_updater()
        assert current_rates == {'USD': {'Value': 100, 'Previous': 90}, 'EUR': {'Value': 110, 'Previous': 100}}
        

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Currency Tracker" in response.data

def test_get_rates_valid_code(client):
    global current_rates
    current_rates =  {
         "USD": {
              "ID": "R01235",
              "NumCode": "840",
              "CharCode": "USD",
              "Nominal": 1,
              "Name": "Доллар США",
              "Value": 93.5142,
              "Previous": 93.6616
             },
           "EUR": {
              "ID": "R01239",
              "NumCode": "978",
              "CharCode": "EUR",
              "Nominal": 1,
              "Name": "Евро",
              "Value": 99.2089,
              "Previous": 99.4007
            }
         }
    response = client.get('/get_rates?currency_code=USD')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['currency_code'] == 'USD'
    assert data['current_rate'] == 93.5142
    assert data['previous_rate'] == 93.6616


def test_get_rates_invalid_code(client):
    response = client.get('/get_rates?currency_code=XYZ')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Invalid currency code'

def test_get_rates_no_code(client):
    response = client.get('/get_rates')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Invalid currency code'