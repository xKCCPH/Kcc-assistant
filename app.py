import os
from flask import Flask, render_template, request
import sqlite3
import re

app = Flask(__name__)

# Kuhanin ang tamang path para mabasa sa Vercel cloud
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'ASND.SQLite3')

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def clean_text(text):
    if not text:
        return ""
    # Tinatanggal ang lahat ng HTML/XML tags tulad ng <pb/>, <i>, </i>
    return re.sub(r'<[^>]+>', '', text)

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Kumuha ng listahan ng lahat ng aklat para sa Table of Contents
    cursor.execute("SELECT book_number, long_name FROM books ORDER BY book_number")
    books = cursor.fetchall()

    raw_verses = []
    verses = []
    query = ""
    selected_book = request.args.get('book', type=int)
    selected_chapter = request.args.get('chapter', type=int)
    chapters = []
    current_book_name = ""

    if selected_book:
        cursor.execute("SELECT long_name FROM books WHERE book_number = ?", (selected_book,))
        b_name_row = cursor.fetchone()
        if b_name_row:
            current_book_name = b_name_row['long_name']

    # 1. Kapag nag-search ng salita mula Genesis hanggang Revelation
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            cursor.execute("""
                SELECT b.long_name, v.chapter, v.verse, v.text 
                FROM verses v 
                JOIN books b ON v.book_number = b.book_number 
                WHERE v.text LIKE ? 
                ORDER BY v.book_number, v.chapter, v.verse
            """, ('%' + query + '%',))
            raw_verses = cursor.fetchall()

    # 2. Kapag pumili ng aklat at kabanata mula sa Table of Contents
    elif selected_book:
        cursor.execute("SELECT DISTINCT chapter FROM verses WHERE book_number = ? ORDER BY chapter", (selected_book,))
        chapters = [row['chapter'] for row in cursor.fetchall()]

        if selected_chapter:
            cursor.execute("""
                SELECT b.long_name, v.chapter, v.verse, v.text 
                FROM verses v 
                JOIN books b ON v.book_number = b.book_number 
                WHERE v.book_number = ? AND v.chapter = ? 
                ORDER BY v.verse
            """, (selected_book, selected_chapter))
            raw_verses = cursor.fetchall()

    conn.close()

    # Linisin ang bawat talata para tanggalin ang mga unwanted tags
    for v in raw_verses:
        v_dict = dict(v)
        v_dict['text'] = clean_text(v_dict['text'])
        verses.append(v_dict)

    return render_template('index.html', books=books, verses=verses, query=query, 
                           selected_book=selected_book, selected_chapter=selected_chapter, 
                           chapters=chapters, current_book_name=current_book_name)

if __name__ == '__main__':
    app.run(debug=True)