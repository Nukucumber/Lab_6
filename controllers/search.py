from app import app
from flask import render_template, request, session, redirect, url_for
from utils import get_db_connection
from models.search_model import get_book, borrow_book, get_genre, get_author, get_publisher

@app.route('/search', methods=["GET"])
def search():
    conn = get_db_connection()

    if request.values.get('borrow_book'):
        book_id = int(request.values.get('borrow_book'))
        borrow_book(conn, book_id, session['reader_id'])
        return redirect(url_for("index"))
    
    
    
    if request.values.get('search') and len(request.values.to_dict()) > 1:
    
        filter_dict = dict(filter(lambda item: item[0] not in ('search'), dict(request.values).items()))
        
        chosen_genre = {}
        chosen_author = {}
        chosen_publisher = {}
        
        df_genre = get_genre(conn)
        df_author = get_author(conn)
        df_publisher = get_publisher(conn)

        for i in range(len(df_genre)):
            if df_genre.loc[i, 'genre_name'] in filter_dict:
                chosen_genre[df_genre.loc[i, 'genre_name']] = df_genre.loc[i, 'genre_id']

        for i in range(len(df_author)):
            if df_author.loc[i, 'author_name'] in filter_dict:
                chosen_author[df_author.loc[i, 'author_name']] = df_author.loc[i, 'author_id']

        for i in range(len(df_publisher)):
            if df_publisher.loc[i, 'publisher_name'] in filter_dict:
                chosen_publisher[df_publisher.loc[i, 'publisher_name']] = df_publisher.loc[i, 'publisher_id']

        df_book = get_book(conn, chosen_genre, chosen_author, chosen_publisher)

        html = render_template(
            'search.html',
            book = df_book,
            genre = df_genre,
            author = df_author,
            publisher = df_publisher,
            chosen_genre = chosen_genre,
            chosen_author = chosen_author,
            chosen_publisher = chosen_publisher,
            len = len
        )
        

    else:
        df_book = get_book(conn)
        df_genre = get_genre(conn)
        df_author = get_author(conn)
        df_publisher = get_publisher(conn)

        html = render_template(
                'search.html',
                book = df_book,
                genre = df_genre,
                author = df_author,
                publisher = df_publisher,
                len = len
        )
        
    return html