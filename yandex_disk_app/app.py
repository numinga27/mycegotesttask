from flask import Flask, request, render_template, redirect, url_for, send_file
import requests
import os

app = Flask(__name__)

# Замените на ваш токен Яндекс.Диска
YANDEX_DISK_TOKEN = 'YOUR_YANDEX_DISK_TOKEN'

def get_files(public_key):
    url = f'https://cloud-api.yandex.net/v1/disk/public/resources?public_key={public_key}'
    headers = {
        'Authorization': f'OAuth {YANDEX_DISK_TOKEN}'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/files', methods=['POST'])
def files():
    public_key = request.form['public_key']
    files_data = get_files(public_key)
    
    if files_data:
        return render_template('files.html', files=files_data['items'])
    else:
        return "Ошибка при получении файлов", 400

@app.route('/download/<file_path>', methods=['GET'])
def download(file_path):
    url = f'https://cloud-api.yandex.net/v1/disk/resources/download?path={file_path}'
    headers = {
        'Authorization': f'OAuth {YANDEX_DISK_TOKEN}'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        download_link = response.json().get('href')
        return redirect(download_link)
    else:
        return "Ошибка при загрузке файла", 400

if __name__ == '__main__':
    app.run(debug=True)
