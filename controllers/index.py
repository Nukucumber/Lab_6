from app import app
from flask import render_template, request, session, redirect, url_for
from utils import get_db_connection
from models.index_model import get_reader, get_book_reader, return_book

@app.route('/', methods=["GET"])
def index():
    conn = get_db_connection()

    if request.values.get('reader'):
        reader_id = int(request.values.get('reader'))
        session['reader_id'] = reader_id
    

    # elif request.values.get('noselect'):
    #     a = 1

    elif request.values.get('return_book'):
        return_book(conn, request.values.get('return_book'))
        return redirect(url_for('index'))

    elif "reader_id" not in session:
        session['reader_id'] = 1
        
    df_reader = get_reader(conn)
    df_book_reader = get_book_reader(conn, session['reader_id'])


    html = render_template(
            'index.html',
            reader_id = session['reader_id'],
            combo_box = df_reader,
            book_reader = df_book_reader,
            len = len
    )
    return html