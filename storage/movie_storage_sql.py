from numpy import integer
from pygments.styles.dracula import comment
from sqlalchemy import create_engine, text
from termcolor import cprint
from pathlib import Path

# Ensure data folder exists
data_path = Path(__file__).resolve().parent.parent / "data"
data_path.mkdir(exist_ok=True)
# Create and return engine
db_file = data_path / "movies.db"
db_url = f"sqlite:///{db_file}"
movie_engine = create_engine(db_url)


def create_table(user_id):
    sql_query = f"""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL ,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL DEFAULT 0.0,
            poster_url TEXT,
            comment DEFAULT ''
        );
    """
    with movie_engine.begin() as conn:
        conn.execute(text(sql_query))
        conn.commit()
    return


def list_movies(user_id):
    """Retrieve all movies from the database."""
    with movie_engine.connect() as movie_connection:
        try:
            result = movie_connection.execute(text(f"SELECT title, year, rating, poster_url, comment FROM movies"),
                                             {"user_id": user_id})
            movies_data = result.fetchall()
            return {row[0]: {"year": row[1], "rating": row[2], "poster_url": row[3], "comment": row[4]} for row in movies_data}
        except Exception as e:
            cprint(f"Error: {e}", 'red')


def add_movie(user_id, title, year, rating, poster_url, comment="" ):
    """Add a new movie to the database."""
    with movie_engine.connect() as movie_connection:
        try:
            movie_connection.execute(text(f"INSERT INTO movies (title, year, rating, poster_url, user_id, comment) VALUES (:title, :year, :rating, :poster_url, :user_id, :comment)"),
                               {"title": title, "year": year, "rating": rating, "poster_url": poster_url, "user_id": user_id, "comment": comment})
            movie_connection.commit()
        except Exception as e:
            cprint(f"Error: {e}", "red")
    return


def delete_movie(title, user_id):
    """Delete a movie from the database."""
    with movie_engine.connect() as movie_connection:
        try:
            movie_connection.execute(text(f"DELETE FROM movies WHERE title = :title AND user_id = :user_id"),
                               {"title": title, "user_id": user_id})
            movie_connection.commit()
        except Exception as e:
            cprint(f"Error: {e}", "red")
    return


def update_movie(title, comment, user_id):
    """Update a movie's rating in the database."""
    with movie_engine.connect() as movie_connection:
        try:
            movie_connection.execute(text(f"UPDATE movies SET comment = :comment WHERE title = :title AND user_id = :user_id"),
                               {"comment": comment, "title": title, "user_id": user_id})
            movie_connection.commit()
        except Exception as e:
            cprint(f"Error: {e}", "red")
    return
