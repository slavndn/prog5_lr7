# Лабораторная работа 7 - Славный Даниил Михайлович 

Необходимо создать программу на языке Python, которая использует паттерн проектирования "Наблюдатель" для отслеживания изменений курсов валют через API Центробанка РФ.

Объект (Subject) будет запрашивать данные с API и отслеживать изменения курсов.
Наблюдатели (Observers) будут получать уведомления об изменении курса и отображать информацию. Например, наблюдателями могут быть различные компоненты системы, которые отслеживают конкретные валюты (например, USD, EUR, GBP).

Серверная часть:
1. Фоновый поток обновляет данные из API Центробанка РФ каждые 10 секунд.
2. Сохраняет текущие курсы в current_rates и предыдущие курсы в previous_rates.

Клиентская часть:
1. Пользователь выбирает валюту и нажимает кнопку "Получить курс".
2. Скрипт отправляет запрос к /get_rates с выбранным кодом валюты.
3. Сервер возвращает текущий курс и курс 10 секунд назад.
4. Данные отображаются в таблице.

![image](https://github.com/user-attachments/assets/87ed6ff7-34d1-42a2-b63d-3b8a20c004a2)

![image](https://github.com/user-attachments/assets/06bd9f66-1509-41e5-9bbf-ef867ebe1dd6)

![image](https://github.com/user-attachments/assets/751cef61-02dc-43d2-8627-78b3f6050b0b)

# Тесты

**1. Импорты:**

```python
import pytest
from app import app, fetch_currency_data, currency_updater, current_rates
import json
import requests_mock
from unittest.mock import patch
```
Тут мы импортируем все необходимое:
    - `pytest`: Это для запуска тестов.
    - `app`: Наше веб-приложение из `app.py`.
    - `fetch_currency_data`: Функция, которая получает данные о валютах.
    - `currency_updater`: Функция, которая обновляет курсы валют.
    - `current_rates`: Глобальная переменная, где хранятся курсы.
    - `json`: Для работы с JSON-данными.
    - `requests_mock`: Для подделки HTTP-запросов.
    - `unittest.mock.patch`: Для подмены других функций, которые мы не хотим вызывать при тестах.

**2. Фикстура `client`:**

```python
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
```
Это фикстура от `pytest`, которая создает тестовый клиент для нашего Flask-приложения. Она:
    - Настраивает приложение на тестовый режим (`app.config['TESTING'] = True`).
    - Создает тестовый клиент (`app.test_client()`).
    - Возвращает этот клиент для использования в тестах (`yield client`).

**3. Тест `test_fetch_currency_data`:**

```python
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
```
Этот тест проверяет функцию `fetch_currency_data`.
    - Он создает моковые данные (как будто с сайта ЦБ РФ пришёл ответ).
    - С помощью `requests_mock.get` он перехватывает запрос к реальному URL и возвращает моковые данные.
    - Вызывает функцию `fetch_currency_data` и сравнивает ее результат с ожидаемыми данными (только блок `Valute`).

**4. Тест `test_currency_updater`:**

```python
def test_currency_updater():
    with patch('app.fetch_currency_data', return_value={'USD': {'Value': 100, 'Previous': 90},
                                                        'EUR': {'Value': 110, 'Previous': 100}}):
        currency_updater()
        assert current_rates == {'USD': {'Value': 100, 'Previous': 90}, 'EUR': {'Value': 110,
                                                        'Previous': 100}}
```
Этот тест проверяет функцию `currency_updater`, которая обновляет курсы.
    - `with patch('app.fetch_currency_data', return_value=...)`: Подменяем функцию `fetch_currency_data` и говорим ей возвращать заранее заданный словарь.
    - Вызываем `currency_updater` и проверяем, что значения в `current_rates` обновились как надо.

**5. Тест `test_index`:**

```python
def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Currency Tracker" in response.data
```
Это тест для главной страницы (`/`).
    - `client.get('/')`: Отправляет GET-запрос на главную страницу.
    - `assert response.status_code == 200`: Проверяет, что страница отвечает с кодом 200 (успешно).
    - `assert b"Currency Tracker" in response.data`: Проверяет, что в ответе есть текст "Currency Tracker".

**6. Тест `test_get_rates_valid_code`:**

```python
def test_get_rates_valid_code(client):
    global current_rates
    current_rates = {
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
```
Это тест для эндпоинта `/get_rates`, когда валюта передана правильно.
    - `global current_rates`: Мы явно задаем словарь с курсами валют для теста.
    - `client.get('/get_rates?currency_code=USD')`: Запрашивает данные для USD.
    - Проверки: статус ответа, код валюты, текущий и предыдущий курс.

**7. Тест `test_get_rates_invalid_code`:**

```python
def test_get_rates_invalid_code(client):
    response = client.get('/get_rates?currency_code=XYZ')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Invalid currency code'
```
Это тест для `/get_rates`, когда валюта невалидна.
    - `client.get('/get_rates?currency_code=XYZ')`: Запрашивает данные для несуществующей валюты.
    - Проверяет, что ответ с кодом 400 и есть сообщение об ошибке.

**8. Тест `test_get_rates_no_code`:**

```python
def test_get_rates_no_code(client):
    response = client.get('/get_rates')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Invalid currency code'
```
Это тест для `/get_rates`, когда вообще не указан код валюты.
    - `client.get('/get_rates')`: Запрашивает без параметра.
    - Проверяет, что ответ с кодом 400 и есть сообщение об ошибке.

**В итоге код:**

- Проверяет, что мы получаем данные о валютах от ЦБ РФ (мокая запрос).
- Обновляем курсы валют.
- Проверяет, что главная страница работает.
- Проверяет `/get_rates` эндпоинт с разными параметрами (валидный код, невалидный, без кода).
