import sqlite3, os

# Configuration
db_name = "newsmead.sqlite"
db_tbl_articles = "articles"
db_insert_query = """
    INSERT INTO {db_tbl_articles}
    (date, category, source, title, author, url, body, image_url, read_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """


def db_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, db_name)


def run_query(conn, query):
    conn.cursor().execute(query)
    conn.commit()


def table_exists(conn, table_name):
    return (
        conn.cursor()
        .execute(
            f"""SELECT name FROM sqlite_master WHERE type='table'
  AND name='{table_name}'; """
        )
        .fetchall()
        != []
    )


def show_table(conn, table_name):
    return conn.execute(f"SELECT * FROM {table_name}").fetchall()


def insert_data(conn, data, insert_query=db_insert_query):
    conn.cursor().executemany(insert_query, data)
    conn.commit()


def db_exists(db_name):
    return os.path.exists(db_path())
