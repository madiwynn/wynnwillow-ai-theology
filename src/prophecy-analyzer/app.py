from flask import Flask, request, jsonify
import sqlite3
import pandas as pd
import re
from datetime import datetime

app = Flask(__name__)

# Initialize a tiny database with example "prophecy" records
def init_db():
    conn = sqlite3.connect('prophecy.db')
    conn.execute(
        '''CREATE TABLE IF NOT EXISTS scriptures 
           (id INTEGER PRIMARY KEY, 
            book TEXT, 
            verse TEXT, 
            keywords TEXT, 
            ai_analysis TEXT, 
            timestamp TEXT)'''
    )
    
    # Example rows just to show structure
    sample_data = [
        ("Revelation", "22:13", "alpha omega eternity",
         "Notes about eternal themes and identity.", 
         "2026-02-22 04:37:00"),
        ("Isaiah", "9:6", "prince peace government",
         "Notes about government, peace, and future hope.", 
         "2026-02-22 04:45:00")
    ]
    
    df = pd.DataFrame(
        sample_data, 
        columns=['book', 'verse', 'keywords', 'ai_analysis', 'timestamp']
    )
    df.to_sql('scriptures', conn, if_exists='replace', index=False)
    conn.close()

@app.route('/analyze', methods=['POST'])
def analyze_prophecy():
    """
    Very simple endpoint:
    - Takes a JSON body with {"verse": "some text"}
    - Extracts a keyword
    - Returns any matching example rows from the tiny database
    """
    verse = request.json.get('verse', '')
    keywords = re.findall(r'\b\w{4,}\b', verse.lower())
    
    if not keywords:
        return jsonify({
            'query': verse,
            'matches': [],
            'message': 'No keywords found in input.'
        })
    
    first_keyword = keywords[0]
    conn = sqlite3.connect('prophecy.db')
    df = pd.read_sql_query(
        "SELECT * FROM scriptures WHERE keywords LIKE ?",
        conn,
        params=(f'%{first_keyword}%',)
    )
    conn.close()
    
    return jsonify({
        'query': verse,
        'matches': df.to_dict('records'),
        'deployed': f"Lampasas, TX - {datetime.now().strftime('%Y-%m-%d %H:%M CST')}",
        'built_by': 'Madison Morris @ Wynn & Willow Co.'
    })

@app.route('/')
def home():
    return {
        'status': 'Wynn & Willow AI-Theology Sample App',
        'location': 'Lampasas, Texas',
        'note': 'This is a simple example for portfolio purposes.'
    }

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)
