import os
from flask import Flask, render_template, request, jsonify
from pypdf import PdfReader
import sqlite3

app = Flask(__name__)

# --- 1. AUTOMATIC KCC PDF KNOWLEDGE LOADER ---
def load_all_kcc_pdfs():
    knowledge_text = ""
    print("Binabasa ang lahat ng KCC PDF files para sa Combot Knowledge Base...")
    for filename in os.listdir('.'):
        if filename.lower().endswith('.pdf'):
            try:
                reader = PdfReader(filename)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        knowledge_text += text + "\n"
            except Exception as e:
                print(f"Error sa pagbasa ng {filename}: {e}")
    return knowledge_text

# I-load ang buong kaalaman mula sa mga PDF sa repository
KCC_KNOWLEDGE_BASE = load_all_kcc_pdfs()

# System prompt directive para kay Combot
COMBOT_SYSTEM_PROMPT = f"""
Ikaw si COMBOT (Kingdom Lens), ang opisyal at matalinong AI Assistant ng Kingdom Community Center (KCC).
Ang iyong layunin ay sagutin ang lahat ng tanong ng mga gumagamit base sa mga opisyal na aralin, katuruan, at PDF documents ng KCC.

MGA GABAY NA PRINSIPYO SA PAGSAGOT:
1. Kingdom Identity & Citizenship: Ang mga mananampalataya ay mga "Citizens" ng Kaharian ng Langit, hindi lamang mga miyembro ng relihiyon. Ang KCC ay isang "Colony" ng langit dito sa lupa.
2. The Bible as the Constitution: Ang Salita ng Diyos (Bibliya) ang ating Saligang Batas (Constitution) na nagpapatakbo sa ating pamumuhay.
3. Kingdom Culture: Isabuhay ang Katwiran (Righteousness), Kapayapaan (Peace), at Kagalakan sa Espiritu Santo. Ang tunay na pag-ibig ay hindi nagtutolerat sa maling gawain.
4. Dominion at Purpose: Ang tao ay nilikha upang mamuno at irepresenta ang Hari (God) sa lupa.
5. Community Unity: Ang kapangyarihan at awtoridad ay dumadaloy sa pamamagitan ng pagkakaisa sa komunidad.

NARITO ANG BUONG MGA ARALIN AT PDF DOCUMENTS BILANG KAHIT ANONG BATAYAN NG IYONG MGA ISASAGOT:
{KCC_KNOWLEDGE_BASE}

Sumagot nang may awtoridad ng Salita, may pagmamahal, at nakabase nang buo sa mga konseptong nakasaad sa itaas.
"""

# --- 2. DATABASE HELPER PARA SA BIBLE APP ---
def query_bible(keyword):
    db_path = 'ASND.SQLite3'
    if not os.path.exists(db_path):
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Hinahanap ang keyword sa ASND database (hal. aklat, talata, o salita)
        query = "SELECT book_name, chapter, verse, text FROM verses WHERE text LIKE ? OR book_name LIKE ? LIMIT 50"
        cursor.execute(query, (f'%{keyword}%', f'%{keyword}%'))
        results = cursor.fetchall()
    except Exception as e:
        results = [("Error", 0, 0, str(e))]
    finally:
        conn.close()
    return results

# --- 3. FLASK ROUTES ---

@app.route('/')
def home():
    # Dito nakalagay ang main landing page mo o kaya ay template ng website
    return render_template('index.html')

@app.route('/bible', methods=['GET', 'POST'])
def bible_app():
    verses = []
    search_query = ""
    if request.method == 'POST':
        search_query = request.form.get('query', '')
        if search_query:
            verses = query_bible(search_query)
    return render_template('bible.html', verses=verses, query=search_query)

@app.route('/api/combot', methods=['POST'])
def combot_api():
    data = request.get_json()
    user_message = data.get('message', '')
    
    # Dito mo ikinakabit ang AI response logic gamit ang COMBOT_SYSTEM_PROMPT at user_message
    # (Maaari itong i-connect sa iyong OpenAI/Gemini API key gamit ang prompt sa itaas)
    
    response_text = f"(Halimbawa ng sagot ni Combot batay sa KCC PDFs para sa tanong na: '{user_message}')"
    
    return jsonify({
        "status": "success",
        "reply": response_text
    })

if __name__ == '__main__':
    app.run(debug=True)
