import json

import pyodbc

from pprint import pprint


server = ''
database = ''
username = ''
password = ''


def create_connection():
    connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                                'SERVER=' + server + ';'
                                'DATABASE=' + database + ';'
                                'UID=' + username + ';'
                                'PWD=' + password)
    return connection


def add_post_data(connection, post_result):
    insert_query = '''INSERT INTO posts_data (creator_post, time_post, link_post, views_post, text_post, photos,
    webpages, documents, videos, audios, name_source, link_source, text_source)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    cursor = connection.cursor()
    cursor.execute(insert_query, post_result)
    connection.commit()


def count_records(connection):
    query = "SELECT * FROM tests LIMIT 5"
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
        return result


if __name__ == "__main__":
    columns = ['id', 'creator_post', 'time_post', 'link_post', 'views_post', 'text_post', 'photos',
               'webpages', 'documents', 'videos', 'audios', 'name_source', 'link_source', 'text_source']

    post_results = []
    connection = create_connection()
    # for post_result in post_results:
    #     add_post_data(connection, post_result)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM posts_data')
    dict = [dict(zip(columns, row)) for row in cursor.fetchall()]
    rows = {"data": dict}
    print(json.dumps(rows, ensure_ascii=False))

    # for row in dict:
    #     print(row)

    connection.close()
