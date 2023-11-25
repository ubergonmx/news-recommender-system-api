import sqlite3, os
from database_utils import table_exists, show_table, run_query, db_exists

# db_name = input("Enter database name: ") + ".sqlite"
# if not db_exists(db_name):
#     if input(f"Database does not exist. Create? (y/n): ") == "n":
#         exit()

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Join the script directory with the database name
db_path = os.path.join(script_dir, db_name)

# Connect to the SQLite database
conn = sqlite3.connect(db_path)

table_name = input("Enter table name: ")

if not (table_exists(conn, table_name)):
    if input(f'Table "{table_name}" does not exist. Create? (y/n): ') == "y":
        # Create the table with the following columns
        # article_id, date, category, source, title, author, url, body, image_url, read_time
        create = f"""
            CREATE TABLE {table_name}
            (
                article_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                category TEXT,
                source TEXT,
                title TEXT,
                author TEXT,
                url TEXT,
                body TEXT,
                image_url TEXT,
                read_time TEXT
            );
            """

        run_query(conn, create)
    else:
        conn.close()
        quit()

while True:
    ans = input(
        "\n\nUSE DB Browser for more features--\n\nWhat do you want to do?\n 1) Show table \n 2) Reset table \n 3) Exit \n\n >"
    )

    if ans == "1":
        print(show_table(conn, table_name))
    elif ans == "2":
        if input("This process is NOT reversible. Are you sure (y/n): ") == "y":
            delete = f"DROP TABLE {table_name}"
            run_query(conn, delete)
            create = f"""
                CREATE TABLE {table_name}
                (
                    article_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    category TEXT,
                    source TEXT,
                    title TEXT,
                    author TEXT,
                    url TEXT,
                    body TEXT,
                    image_url TEXT,
                    read_time TEXT
                );
                """
            run_query(conn, create)

        print(f'Reset "{table_name}".')
        conn.close()
        exit()

    elif ans == "3":
        conn.close()
        quit()
