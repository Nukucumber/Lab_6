from app import app
from flask import render_template, request, session, redirect, url_for
from utils import get_db_connection
from models.index_model import get_new_reader

@app.route('/new_reader', methods=["GET"])
def new_reader():
    conn = get_db_connection()

    if request.values.get("cancel"):
        return redirect(url_for("index"))

    if request.values.get("add") and request.values.get("new_reader"):
        new_reader = request.values.get('new_reader')
        session['reader_id'] = get_new_reader(conn, new_reader)
        return redirect(url_for("index"))

    html = render_template(
        'new_reader.html'
    )
    return html