import pandas

def get_reader(conn):
    return pandas.read_sql('''

        SELECT * FROM reader
    
    ''', conn)

def get_book_reader(conn, reader_id):
    return pandas.read_sql('''

        WITH get_authors( book_id, authors_name)
        AS(
            SELECT book_id, GROUP_CONCAT(author_name)
            FROM author JOIN book_author USING(author_id)
            GROUP BY book_id
        )
        SELECT title AS Название, authors_name AS Авторы,
            borrow_date AS Дата_выдачи, return_date AS Дата_возврата,
            book_reader_id
        FROM
            reader
            JOIN book_reader USING(reader_id)
            JOIN book USING(book_id)
            JOIN get_authors USING(book_id)
        WHERE reader.reader_id = :id
        ORDER BY 3

    
    ''', conn, params={"id": reader_id})

def get_new_reader(conn, new_reader):
    cur = conn.cursor()
    cur.execute('''

        insert into reader (reader_id, reader_name) values (null, :new_reader)

    ''', {"new_reader": new_reader})
    conn.commit()
    cur.close()
    
    return cur.lastrowid

def return_book(conn, book_reader_id):
    cur = conn.cursor()
    
    cur.execute('''
                
        update book as A
        set available_numbers = A.available_numbers + 1
        from book as B join book_reader using (book_id)   
        where book_reader_id = :curr_book_reader_id
        and A.book_id = B.book_id;
                
        
                                     
    ''', {"curr_book_reader_id": book_reader_id})

    cur.execute('''
                
        update book_reader
        set return_date = date('now', 'localtime')
        where book_reader_id = :curr_book_reader_id
                                     
    ''', {"curr_book_reader_id": book_reader_id})

    conn.commit()

    cur.close()
    
    return