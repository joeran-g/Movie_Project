from sqlalchemy import create_engine, text
from termcolor import cprint
from pathlib import Path

def set_engine(user_data):
    """
    Creates the data folder, if it doesn't exist and returns the engine for the user
    """
    user_id, user_name = user_data
    # Ensure data folder exists
    data_path = Path(__file__).resolve().parent.parent / "data"
    data_path.mkdir(exist_ok=True)
    # Create and return engine
    db_file = data_path / f"{user_id}_movies.db"
    db_url = f"sqlite:///{db_file}"
    return create_engine(db_url)


def create_table(user_data, engine):
    user_id, user_name = user_data
    sql_query = f"""
        CREATE TABLE IF NOT EXISTS "{user_id}_movies" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL DEFAULT 0.0,
            poster_url TEXT,
            comment DEFAULT ''
        );
    """
    with engine.begin() as conn:
        conn.execute(text(sql_query))
        conn.commit()
    return


def delete_user_table(user_data, engine):
    """ Delete an existing table, if a user decides to delete his account"""
    user_id, user_name = user_data
    sql_query = f"""
            DROP TABLE "{user_id}_movies"
            );
        """
    with engine.begin() as conn:
        conn.execute(text(sql_query))
        conn.commit()
    return


def list_movies(user_data, engine):
    """Retrieve all movies from the database."""
    user_id, user_name = user_data
    table_name = f"{user_id}_movies"
    with engine.connect() as movie_connection:
        try:
            result = movie_connection.execute(text(f"SELECT title, year, rating, poster_url FROM '{table_name}'"),
                                             {"user_id": user_id})
            movies_data = result.fetchall()
            return {row[0]: {"year": row[1], "rating": row[2], "poster_url": row[3]} for row in movies_data}
        except Exception as e:
            cprint(f"Error: {e}", 'red')




def add_movie(title, year, rating, poster_url, user_data, engine):
    """Add a new movie to the database."""
    user_id, user_name = user_data
    table_name = f"{user_id}_movies"
    with engine.connect() as movie_connection:
        try:
            movie_connection.execute(text(f"INSERT INTO '{table_name}' (title, year, rating, poster_url) VALUES (:title, :year, :rating, :poster_url)"),
                               {"title": title, "year": year, "rating": rating, "poster_url": poster_url})
            movie_connection.commit()
        except Exception as e:
            cprint(f"Error: {e}", "red")
    return


def delete_movie(title, user_data, engine):
    """Delete a movie from the database."""
    user_id, user_name = user_data
    table_name = f"{user_id}_movies"
    with engine.connect() as movie_connection:
        try:
            movie_connection.execute(text(f"DELETE FROM '{table_name}' WHERE title = :title"),
                               {"title": title})
            movie_connection.commit()
        except Exception as e:
            cprint(f"Error: {e}", "red")
    return


def update_movie(title, comment, user_data, engine):
    """Update a movie's rating in the database."""
    user_id, user_name = user_data
    table_name = f"{user_id}_movies"
    with engine.connect() as movie_connection:
        try:
            movie_connection.execute(text(f"UPDATE '{table_name}' SET comment = :comment WHERE title = :title"),
                               {"comment": comment, "title": title})
            movie_connection.commit()
        except Exception as e:
            cprint(f"Error: {e}", "red")
    return
