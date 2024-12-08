from flask import Flask, render_template, jsonify, request
import requests
import threading
import time

app = Flask(__name__)

# Переменные для хранения данных
current_rates = {}
previous_rates = {}

def fetch_currency_data():
    """Получение данных о курсах валют из API Центробанка РФ"""
    response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
    return response.json().get('Valute', {})

def currency_updater():
    """Обновление курсов валют каждые 10 секунд"""
    global current_rates, previous_rates
    while True:
        new_rates = fetch_currency_data()
        if current_rates:  # Сохраняем текущие курсы как предыдущие
            previous_rates = current_rates
        current_rates = new_rates  # Обновляем текущие курсы
        time.sleep(10)  # Задержка в 10 секунд

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/get_rates', methods=['GET'])
def get_rates():
    """Возвращает текущие и предыдущие курсы валют"""
    global current_rates, previous_rates
    currency_code = request.args.get('currency_code')  # Получаем код валюты из запроса
    if not currency_code or currency_code not in current_rates:
        return jsonify({'error': 'Invalid currency code'}), 400

    current_rate = current_rates[currency_code]
    previous_rate = previous_rates.get(currency_code, {'Value': None, 'Previous': None})
    return jsonify({
        'currency_code': currency_code,
        'current_rate': current_rate['Value'],
        'previous_rate': previous_rate['Value'] or current_rate['Previous']
    })

# Запуск фонового процесса
threading.Thread(target=currency_updater, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True)
