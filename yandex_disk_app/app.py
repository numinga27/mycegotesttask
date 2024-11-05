from flask import session
from flask import Flask, render_template, request, redirect, url_for, send_file
from urllib.parse import quote
import requests
import os
import httpx
import logging

app = Flask(__name__)
app.secret_key = 'ваш_секретный_ключ'

# Конфигурация
CLIENT_ID = '5866363715854fd0908bbb08fe690b88'  # Замените на ваш client_id
CLIENT_SECRET = 'aa8baf12ccc947619ed55f821449e8a3'  # Замените на ваш client_secret
REDIRECT_URI = 'http://localhost:5000/callback'
TOKEN = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/auth')
def auth():
    return redirect(f'https://oauth.yandex.ru/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}')


@app.route('/callback')
def callback():
    global TOKEN
    code = request.args.get('code')

    token_url = 'https://oauth.yandex.ru/token'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI
    }

    response = requests.post(token_url, data=data)

    if response.status_code == 200:
        token_info = response.json()
        TOKEN = token_info['access_token']
        return redirect(url_for('file_list'))
    else:
        # Отладочное сообщение
        print(
            f"Error obtaining token: {response.status_code}, {response.text}")
        return "Ошибка при получении токена", 400


@app.route('/files', methods=['GET', 'POST'])
def file_list():
    if request.method == 'POST':
        if not TOKEN:
            return "Токен не получен", 400

        public_key = request.form.get('public_key')
        if not public_key:
            return "Публичный ключ не указан", 400

        # Сохраняем public_key в сессии
        session['public_key'] = public_key

        headers = {'Authorization': f'OAuth {TOKEN}'}
        url = f'https://cloud-api.yandex.net/v1/disk/public/resources?public_key={public_key}'

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            files = response.json().get('_embedded', {}).get('items', [])
            return render_template('file_list.html', files=files)
        else:
            return f"Ошибка при получении файлов: {response.status_code}", 400

    return render_template('file_list.html')


@app.route('/download/<path:file_name>')
async def download(file_name):
    # Получаем public_key из сессии
    public_key = session.get('public_key')
    if not public_key:
        return "Публичный ключ не найден", 400

    headers = {'Authorization': f'OAuth {TOKEN}'}
    encoded_file_name = quote(file_name)  # Кодируем имя файла
    url = f'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={public_key}&path={encoded_file_name}'

    logging.info(f"Запрашиваем URL: {url} с токеном: {TOKEN}")

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        if response.status_code == 200:
            download_url = response.json().get('href')
            return redirect(download_url)
        else:
            logging.error(
                f"Ошибка при получении ссылки для скачивания: {response.text}")
            return f"Ошибка при получении ссылки для скачивания: {response.text}", 400



if __name__ == '__main__':
    app.run(debug=True)
