from flask import Flask, render_template, request, redirect, url_for, send_file
import requests
import os

app = Flask(__name__)

# Конфигурация
CLIENT_ID = '5866363715854fd0908bbb08fe690b88'  # Замените на ваш client_id
CLIENT_SECRET = 'aa8baf12ccc947619ed55f821449e8a3'  # Замените на ваш client_secret
REDIRECT_URI = 'https://disk.yandex.ru/client/disk'
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
        return "Ошибка при получении токена", 400


@app.route('/files', methods=['GET', 'POST'])
def file_list():
    if request.method == 'POST':
        public_key = request.form['public_key']
        headers = {'Authorization': f'OAuth {TOKEN}'}
        url = f'https://cloud-api.yandex.net/v1/disk/public/resources?public_key={public_key}'

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            files = response.json().get('_embedded', {}).get('items', [])
            return render_template('index.html', files=files)
        else:
            return "Ошибка при получении файлов", 400

    return render_template('index.html')


@app.route('/download/<file_name>')
def download(file_name):
    headers = {'Authorization': f'OAuth {TOKEN}'}
    url = f'https://cloud-api.yandex.net/v1/disk/resources/download?path={file_name}'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        download_url = response.json().get('href')
        return redirect(download_url)
    else:
        return "Ошибка при получении ссылки для скачивания", 400


if __name__ == '__main__':
    app.run(debug=True)
