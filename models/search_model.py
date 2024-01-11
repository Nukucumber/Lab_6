import pandas

def get_book(conn, chosen_genre = {}, chosen_author = {}, chosen_publisher = {}):
    if len(chosen_genre) == 0 and len(chosen_author) == 0 and len(chosen_publisher) == 0:
        return pandas.read_sql('''
                            
            WITH get_authors( book_id, authors_name)
            AS(
                SELECT book_id, GROUP_CONCAT(author_name, ', ')
                FROM author JOIN book_author USING(author_id)
                GROUP BY book_id
            )

            select
                title as Название, 
                authors_name as 'Авторы', 
                genre_name as Жанр,
                publisher_name as Издательство,
                year_publication as Год_издания,
                available_numbers as Количество,
                book_id
            from book join genre using(genre_id) 
            join publisher using(publisher_id) 
            join get_authors using(book_id)

        ''', conn)
    else:
        cur = conn.cursor()

        df_genre = pandas.DataFrame()
        for item in chosen_genre:
            df_tmp = pandas.DataFrame(cur.execute('''
                
                select book_id from book
                where genre_id = :item

            ''', {"item": int(chosen_genre[item])}))

            df_genre = pandas.concat([df_genre, df_tmp])
        df_genre.reset_index(inplace = True, drop= True)
        df_genre = [df_genre.loc[i, 0] for i in range(len(df_genre))] if len(df_genre) != 0 else []
            

        df_author = pandas.DataFrame()
        for item in chosen_author:
            df_tmp = pandas.DataFrame(cur.execute('''
                
                select book_id from book_author
                where author_id = :item

            ''', {"item": int(chosen_author[item])}))
                
            df_author = pandas.concat([df_author, df_tmp])
        df_author.reset_index(inplace = True, drop = True)
        df_author = [df_author.loc[i, 0] for i in range(len(df_author))] if len(df_author) != 0 else []


        df_publisher = pandas.DataFrame()
        for item in chosen_publisher:
            df_tmp = pandas.DataFrame(cur.execute('''
                
                select book_id from book
                where publisher_id = :item

            ''', {"item": int(chosen_publisher[item])}))
                
            df_publisher = pandas.concat([df_publisher, df_tmp])
        df_publisher.reset_index(inplace = True, drop = True)
        if len(df_genre) != 0:
            df_publisher = [df_publisher.loc[i, 0] for i in range(len(df_publisher))] if len(df_publisher) != 0 else []


        index = df_genre if len(df_genre) != 0 else []
        index = df_author if len(df_author) != 0 else index
        index = df_publisher if len(df_publisher) != 0 else index
        index = list(set(index) & set(df_genre)) if len(df_genre) != 0 else index
        index = list(set(index) & set(df_author)) if len(df_author) != 0 else index
        index = list(set(index) & set(df_publisher)) if len(df_publisher) != 0 else index

        print(index)

        df = pandas.DataFrame()
        for item in index:

            df_tmp = pandas.read_sql('''
                            
                WITH get_authors( book_id, authors_name)
                AS(
                    SELECT book_id, GROUP_CONCAT(author_name, ', ')
                    FROM author JOIN book_author USING(author_id)
                    GROUP BY book_id
                )

                select
                    title as Название, 
                    authors_name as 'Авторы', 
                    genre_name as Жанр,
                    publisher_name as Издательство,
                    year_publication as Год_издания,
                    available_numbers as Количество,
                    book_id
                from book join genre using(genre_id) 
                join publisher using(publisher_id) 
                join get_authors using(book_id)
                where book_id = :item

            ''', conn, params = {"item": int(item)})  

            df = pandas.concat([df, df_tmp])

        df.reset_index(inplace = True, drop= True)
        return df
    
def get_genre(conn):

    return pandas.read_sql('''
                           
        select distinct genre.*, count() over(partition by book.genre_id) as count from genre join book using(genre_id)

    ''', conn)

def get_author(conn):
    return pandas.read_sql('''
                           
        select distinct author.*, count() over(partition by book_author.author_id)
        as count from author join book_author using(author_id)

    ''', conn)

def get_publisher(conn):
    return pandas.read_sql('''
                           
        select distinct publisher.*, count() over(partition by publisher_id) 
        as count from publisher join book using(publisher_id)

    ''', conn)

def borrow_book(conn, book_id, reader_id):
    cur = conn.cursor()

    cur.execute('''
        
        insert into book_reader (book_reader_id, book_id, reader_id, borrow_date, return_date) values (null, :curr_book_id, :curr_reader_id, date('now', 'localtime'), null)

    ''', {"curr_book_id": book_id, "curr_reader_id": reader_id})

    cur.execute('''
        
        update book
        set available_numbers = available_numbers - 1
        where book_id = :curr_book_id

    ''', {"curr_book_id": book_id})

    conn.commit()

    cur.close()

    return True