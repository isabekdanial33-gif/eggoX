from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
# Включаем CORS, чтобы Netlify мог спокойно общаться с Railway
CORS(app, resources={r"/*": {"origins": "*"}}) 

# Насильно вшиваем заголовки CORS во все ответы для подстраховки
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

# Временное хранилище сообщений в памяти сервера
messages = []

# Главная страница (проверка для Railway)
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "alive", "messages_count": len(messages)}), 200

# Маршрут для отправки и получения сообщений
@app.route('/generate', methods=['POST', 'GET', 'OPTIONS'])
def generate():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    # Если твой фронтенд на Netlify делает GET-запрос, чтобы забрать сообщения
    if request.method == 'GET':
        return jsonify({"messages": messages}), 200

    # Если фронтенд делает POST-запрос, чтобы отправить новое сообщение
    data = request.json
    if not data:
        return jsonify({"error": "Нет данных запроса"}), 400
        
    prompt = data.get('prompt', '') # Оставляем 'prompt', так как на Netlify кнопка шлёт это поле
    if not prompt:
        return jsonify({"error": "Пустое сообщение"}), 400

    # Сохраняем сообщение
    messages.append(prompt)

    # Возвращаем ответ фронтенду, чтобы на экране появилось сообщение
    # Можешь изменить "result" на то, что ожидает твой JS код (например, эхо-ответ или статус)
    return jsonify({
        "result": f"Сообщение получено: {prompt}",
        "status": "success"
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
