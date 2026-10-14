import os
from flask import Flask, render_template, request, jsonify
from pypdf import PdfReader
from google import genai

app = Flask(__name__, template_folder='.')

# System Persona at Guidelines para kay Combot
COMBOT_SYSTEM_PROMPT = """
Tawag kay Combot, ang opisyal na AI Assistant ng Kingdom Citizen Church (KCC).
Ang iyong misyon ay magbigay ng kaalaman, gabay, at karunungan na nakabase sa KCC Doctrine, Kingdom Identity, Citizenship, at Constitution ng Kaharian ng Diyos.

MGA ALITUNTUNIN SA PAGSAGOT:
1. Regulasyon, pinapangunahan, at may awtoridad ng isang Kingdom Citizen ang iyong pananalita.
2. Gamitin ang iyong "Knowledge Base" mula sa mga PDF documents bilang pangunahing batayan ng iyong mga sagot.
3. Kung may tinatayimang na aralin sa KCC Doctrine o Kingdom materials, sundin ito gamit ang pangkalahatang prinsipyo ng Kaharian ngunit linawin na itong ay nakabatay sa Kingdom perspective.
4. Maging malinaw, direkta, at nakakapagbigay ng pananampalataya at pagkakakilanlan (Kingdom Identity).
"""

def load_all_local_pdfs():
    """Binabasa ang lahat ng PDF files sa buong repository at pinagsasama sa isang text base."""
    combined_text = ""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    for root, dirs, files in os.walk(current_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                try:
                    reader = PdfReader(pdf_path)
                    combined_text += f"\n--- DOCUMENT: {file} ---\n"
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            combined_text += extracted + "\n"
                except Exception as e:
                    print(f"Error reading {file}: {e}")
                    
    return combined_text

# I-load ang mga PDF kapag nag-start ang server
KCC_KNOWLEDGE_BASE = load_all_local_pdfs()

# Initialize Gemini Client (Awtomatikong kukuha ng GEMINI_API_KEY mula sa Vercel environment variables)
client = genai.Client()

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

        # Pagsasamahin ang System Prompt, PDF Knowledge Base, at Tanong ng User
        full_prompt = f"""
{COMBOT_SYSTEM_PROMPT}

MGA DOKUMENTO AT ARALIN (KCC KNOWLEDGE BASE):
{KCC_KNOWLEDGE_BASE}

TANONG NG USER:
{user_message}
"""

        # Paggamit ng tamang Google GenAI SDK syntax
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
