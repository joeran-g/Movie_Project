import json


def get_movies():
    """
    Returns a dictionary of dictionaries that
    contains the movies information in the database.
    The function loads the information from the SQL
    file and returns the data.
    """
    with open("movies_data.json", "r", encoding='utf-8') as movie_data:
        movies_dict = json.loads(movie_data.read())
    return movies_dict


def save_movies(movies):
    """
    Gets all your movies as an argument and saves them to the SQL file.
    """
    with open("movies_data.json", "w") as data:
        json.dump(movies, data)


def add_movie(title, year, rating):
    """
    Adds a movie to the movies database.
    Loads the information from the sql file, add the movie,
    and saves it. The function doesn't need to validate the input.
    """
    movies_dict = get_movies()
    movies_dict[title] = {
        "title": title,
        "rating": rating,
        "year": year
    }
    save_movies(movies_dict)


def delete_movie(title):
    """
    Deletes a movie from the movies database.
    Loads the information from the JSON file, deletes the movie,
    and saves it. The function doesn't need to validate the input.
    """
    movies_dict = get_movies()
    if title in movies_dict:
        del movies_dict[title]
    save_movies(movies_dict)


def update_movie(title, rating):
    """
    Updates a movie from the movies database.
    Loads the information from the JSON file, updates the movie,
    and saves it. The function doesn't need to validate the input.
    """
    movies_dict = get_movies()
    if title in movies_dict:
        movies_dict[title]['rating'] = rating
    save_movies(movies_dict)
