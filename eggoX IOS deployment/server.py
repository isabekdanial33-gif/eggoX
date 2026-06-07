from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from deep_translator import GoogleTranslator

app = Flask(__name__)
CORS(app) # Разрешаем Netlify общаться с сервером

def is_cyrillic(text):
    return bool(re.search('[а-яА-ЯёЁ]', text))

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({"error": "Пустой запрос"}), 400

        # Твоя логика проверки языка
        is_ru = is_cyrillic(prompt)
        
        # Перевод на английский
        if is_ru:
            prompt_en = GoogleTranslator(source='ru', target='en').translate(prompt)
        else:
            prompt_en = prompt

        # Вместо запроса к Хаггинг Фейсу — ответ от твоего собственного сервера
        ai_text_en = f"This is a response from your own server! You said: {prompt_en}"
        
        # Перевод обратно на русский
        if is_ru:
            ai_text_final = GoogleTranslator(source='en', target='ru').translate(ai_text_en)
        else:
            ai_text_final = ai_text_en
            
        return jsonify({"result": ai_text_final})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)