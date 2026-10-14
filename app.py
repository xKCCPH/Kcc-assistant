import os
from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__, template_folder='.')

# System Persona at Guidelines para kay Combot
COMBOT_SYSTEM_PROMPT = """
Tawag kay Combot, ang opisyal na AI Assistant ng Kingdom Citizen Church (KCC).
Ang iyong misyon ay magbigay ng kaalaman, gabay, at karunungan na nakabase sa KCC Doctrine, Kingdom Identity, Citizenship, at Constitution ng Kaharian ng Diyos.

MGA ALITUNTUNIN SA PAGSAGOT:
1. Regulasyon, pinapangunahan, at may awtoridad ng isang Kingdom Citizen ang iyong pananalita.
2. Gamitin ang iyong kaalaman ukol sa KCC Doctrine at Kingdom materials bilang pangunahing batayan ng iyong mga sagot.
3. Maging malinaw, direkta, at nakakapagbigay ng pananampalataya at pagkakakilanlan (Kingdom Identity).
"""

# Initialize Gemini Client (Awtomatikong kukuha ng GEMINI_API_KEY mula sa Vercel environment variables)
try:
    client = genai.Client()
except Exception as e:
    print(f"GenAI Client Init Error: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/bible')
def bible():
    return render_template('bible.html')

@app.route('/api/combot', methods=['POST'])
def combot_api():
    try:
        data = request.get_json() or {}
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({"status": "error", "reply": "Mangyaring magbigay ng tanong o mensahe."}), 400

        # Pagsasamahin ang System Prompt at Tanong ng User
        full_prompt = f"""
{COMBOT_SYSTEM_PROMPT}

TANONG NG USER:
{user_message}
"""

        # Paggamit ng Google GenAI API
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt
        )

        response_text = response.text

        return jsonify({
            "status": "success",
            "reply": response_text
        })

    except Exception as e:
        print(f"Combot API Error: {e}")
        return jsonify({
            "status": "error",
            "reply": f"Paumanhin, nagkaroon ng pansamantalang suliranin sa pagpoproseso ng iyong hiling: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
