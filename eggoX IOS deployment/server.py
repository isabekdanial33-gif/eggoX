from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
from deep_translator import GoogleTranslator

app = Flask(__name__)
CORS(app) # Разрешаем твоему HTML-файлу общаться с этим скриптом

import os
# Вместо прямого текста теперь берем ключ из защищенной переменной
HF_TOKEN = os.getenv("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}
API_URL = "https://api-inference.huggingface.co/models/TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Функция для определения русского языка (ищет кириллицу)
def is_cyrillic(text):
    return bool(re.search('[а-яА-ЯёЁ]', text))

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({"error": "Пустой запрос"}), 400

    # 1. Автоопределение языка
    is_ru = is_cyrillic(prompt)
    
    # 2. Перевод на английский (ИИ думает на нем лучше всего)
    if is_ru:
        prompt_en = GoogleTranslator(source='ru', target='en').translate(prompt)
    else:
        prompt_en = prompt

    # 3. Запрос к TinyLlama
    payload = {
        "inputs": f"<|system|>\nYou are a helpful AI assistant.</s>\n<|user|>\n{prompt_en}</s>\n<|assistant|>\n"
    }
    
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        
        if response.status_code != 200:
            return jsonify({"error": f"Ошибка сервера ИИ: {response.status_code}"}), 500
            
        raw_text = response.json()[0]['generated_text']
        ai_text_en = raw_text.split("<|assistant|>\n")[-1].strip()
        
        # 4. Перевод обратно на русский, если изначальный запрос был на русском
        if is_ru:
            ai_text_final = GoogleTranslator(source='en', target='ru').translate(ai_text_en)
        else:
            ai_text_final = ai_text_en
            
        return jsonify({"result": ai_text_final})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render автоматически назначает порт через переменную среды PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)