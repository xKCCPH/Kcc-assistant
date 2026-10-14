import os
from flask import Flask, render_template, request
import sqlite3
import re

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'ASND.SQLite3')

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'<[^>]+>', '', text)

# Dito natin inilagay sa /bible path para hindi masapawan ang main home page ninyo
@app.route('/bible', methods=['GET', 'POST'])
def bible():
    conn = get_db_connection()
    cursor = conn.cursor()
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

    for v in raw_verses:
        v_dict = dict(v)
        v_dict['text'] = clean_text(v_dict['text'])
        verses.append(v_dict)

    return render_template('index.html', books=books, verses=verses, query=query, 
                           selected_book=selected_book, selected_chapter=selected_chapter, 
                           chapters=chapters, current_book_name=current_book_name)

# Pwedeng magdagdag ng simpleng welcome page para sa mismong main link (/)
@app.route('/')
def home():
    return """
    <div style="font-family: Arial; text-align: center; margin-top: 100px;">
        <h1>Welcome to Kingdom Community Center</h1>
        <p>I-click ang button sa ibaba para buksan ang ASND Bible Studio:</p>
        <a href="/bible" style="display: inline-block; padding: 15px 30px; background-color: #2b6cb0; color: white; text-decoration: none; border-radius: 8px; font-size: 18px; font-weight: bold;">📖 Buksan ang ASND Bible</a>
    </div>
    """

if __name__ == '__main__':
    app.run(debug=True)
