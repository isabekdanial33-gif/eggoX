from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
from deep_translator import GoogleTranslator
import os

app = Flask(__name__)
# Включаем CORS для всех запросов
CORS(app, resources={r"/*": {"origins": "*"}}) 

# ЖЕСТКИЙ ХАК: Насильно вшиваем CORS во все ответы сервера
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

# СПАСИТЕЛЬНЫЙ МАРШРУТ ДЛЯ RAILWAY (Health Check)
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "alive", "message": "Server is running perfectly!"}), 200

HF_TOKEN = os.getenv("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}
API_URL = "https://api-inference.huggingface.co/models/TinyLlama/TinyLlama-1.1B-Chat-v1.0"

def is_cyrillic(text):
    return bool(re.search('[а-яА-ЯёЁ]', text))

@app.route('/generate', methods=['POST', 'OPTIONS'])
def generate():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    data = request.json
    if not data:
        return jsonify({"error": "Нет данных запроса"}), 400
        
    prompt = data.get('prompt', '')
    if not prompt:
        return jsonify({"error": "Пустой запрос"}), 400

    is_ru = is_cyrillic(prompt)
    
    if is_ru:
        try:
            prompt_en = GoogleTranslator(source='ru', target='en').translate(prompt)
        except Exception as e:
            return jsonify({"error": f"Ошибка переводчика (RU->EN): {str(e)}"}), 500
    else:
        prompt_en = prompt

    payload = {
        "inputs": f"<|system|>\nYou are a helpful AI assistant.</s>\n<|user|>\n{prompt_en}</s>\n<|assistant|>\n"
    }
    
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        
        if response.status_code != 200:
            return jsonify({"error": f"Ошибка сервера ИИ: {response.status_code}", "details": response.text}), 500
            
        res_json = response.json()
        raw_text = res_json[0]['generated_text']
        ai_text_en = raw_text.split("<|assistant|>\n")[-1].strip()
        
        if is_ru:
            ai_text_final = GoogleTranslator(source='en', target='ru').translate(ai_text_en)
        else:
            ai_text_final = ai_text_en
            
        return jsonify({"result": ai_text_final})
        
    except Exception as e:
        return jsonify({"error": f"Внутренняя ошибка сервера: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
