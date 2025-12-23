from sqlalchemy import create_engine, text
from termcolor import cprint


def set_engine(user_id):
    # Define the database URL
    db_url = f"sqlite:///../data/{user_id}_movies.db"
    # Return the engine
    engine = create_engine(db_url)
    return engine

def create_table(user_id):
    engine = set_engine(user_id)
    # Create the movies table if it does not exist
    with engine.connect() as connection:
        with engine.connect() as connection:
            connection.execute(text(f"""
                                    CREATE TABLE IF NOT EXISTS {user_id}_movies
                                    (
                                        id         INTEGER PRIMARY KEY AUTOINCREMENT,
                                        title      TEXT UNIQUE NOT NULL,
                                        year       INTEGER     NOT NULL,
                                        rating     REAL        NOT NULL DEFAULT 0.0,
                                        poster_url TEXT,
                                        user_id INTEGER FOREIGN KEY DEFAULT {user_id}
                                    );
                                    """))
        connection.commit()



def list_movies(user_id, user_name):
    """Retrieve all movies from the database."""
    engine = set_engine(user_id)
    with engine.connect() as connection:
        result = connection.execute(text(f"SELECT title, year, rating, poster_url FROM {user_name}_movies"))
        movies = result.fetchall()
    return {row[0]: {"year": row[1], "rating": row[2], "poster_url": row[3]} for row in movies}


def add_movie(title, year, rating, poster_url, user_id, user_name):
    """Add a new movie to the database."""
    engine = set_engine(user_id)
    with engine.connect() as connection:
        try:
            connection.execute(text(f"INSERT INTO {user_name}_movies (title, year, rating, poster_url) VALUES (:title, :year, :rating, :poster_url)"),
                               {"title": title, "year": year, "rating": rating, "poster_url": poster_url})
        except Exception as e:
            cprint(f"Error: {e}", "red")


def delete_movie(title, user_id, user_name):
    engine = set_engine(user_id)
    """Delete a movie from the database."""
    with engine.connect() as connection:
        try:
            connection.execute(text(f"DELETE FROM {user_name}_movies WHERE title = :title"),
                               {"title": title})
        except Exception as e:
            cprint(f"Error: {e}", "red")


def update_movie(title, rating, user_id, user_name):
    """Update a movie's rating in the database."""
    engine = set_engine(user_id)
    with engine.connect() as connection:
        try:
            connection.execute(text(f"UPDATE {user_name}_movies SET rating = :rating WHERE title = :title"),
                               {"rating": rating, "title": title})
        except Exception as e:
            cprint(f"Error: {e}", "red")
