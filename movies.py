# Added Libraries
import random
import matplotlib.pyplot as plt
from termcolor import colored, cprint
from rapidfuzz.fuzz import partial_ratio as _partial_ratio
from urllib3.exceptions import RequestError
import movie_storage_sql as storage
import api_data_handling as api


FIRST_MOVIE_YEAR = 1895
CURRENT_YEAR = 2025


def show_menu(choices_dict):
    cprint("Menu:", 'cyan')
    choice_num = 0
    for choice in choices_dict:
        cprint(f"{choice_num}. {choice['name']}", 'green')
        choice_num += 1


def list_movies(movies_dict):
    cprint(f"\n{len(movies_dict)} movies in total", 'cyan')
    for movie, stats in movies_dict.items():
        print(f"{movie} ({stats['year']}), {stats['rating']}")


def get_movie_name(menu_option="work with"):
    """
    Ask the user for a movie name until he enters a string.
    optional string input for options
    """
    while True:
        name = input(colored(f"Enter movie name to {menu_option}: ", 'yellow'))
        if not name:
            cprint("Invalid name!", 'red')
            continue
        return name.title()


def add_movie(movies_dict):
    """
    Get a movie name by the user,
    if the movie exists in the OMDb-API, fetch the data.
    add the new movie, rating, year and image-url to the sql database.
    """
    movie = get_movie_name("add").title()
    if movie not in movies_dict:
        try:
            movie_data = api.get_movie_by_title(movie)
            print(movie_data)
            movie_rating = movie_data["imdbRating"]
            movie_year = movie_data["Year"]
            movie_img_url = movie_data["Poster"]
            storage.add_movie(movie, movie_year, movie_rating, movie_img_url)
            cprint(f"Movie '{movie}' successfully added!", 'cyan')
        except RequestError:
            cprint(f"Could not request movie named: {movie}", 'red')
        except ConnectionError:
            cprint("No connection to the api", 'red')
    else:
        cprint("This movie was already saved.", 'red')


def delete_movie(movies_dict):
    """Ask user for a movie, if it exists. delete it from the sql database"""
    movie_to_delete = get_movie_name("delete").title()
    if movie_to_delete not in movies_dict:
        cprint(f"Movie '{movie_to_delete}' doesn't exist!", 'red')
    else:
        storage.delete_movie(movie_to_delete)
        cprint(f"Movie '{movie_to_delete}' successfully deleted", 'cyan')


def update_movie(movies_dict):
    """
    Update the rating of a existing Movie from the sql database
    and check for wrong inputs
    """
    movie_to_update = get_movie_name("update")
    if movie_to_update in movies_dict:
        new_rating = get_rating()
        storage.update_movie(movie_to_update, new_rating)
        cprint(f"Movie '{movie_to_update}' successfully updated!", 'cyan')
    else:
        cprint(f"Movie '{movie_to_update}' doesn't exist!", 'red')


def show_stats(movies_dict):
    """
    Get the values of a dictionary and show average/median value
    and the best/worst value/s
    show an error and return if a wrong value is given
    """
    if not movies_dict:
        cprint("No movies found!", 'red')
        return
    ratings_list = [stats['rating'] for stats in movies_dict.values()]
    # Average value + DivisionError check
    try:
        average_rating = sum(ratings_list) / len(ratings_list)
    except ZeroDivisionError:
        cprint("No ratings found!", 'red')
        return
    print(f"Average rating: {round(average_rating, 1)}")
    # Median value
    middle_of_list = len(ratings_list) // 2
    median_value = (ratings_list[middle_of_list] + ratings_list[~middle_of_list]) / 2
    print(f"Median rating: {round(median_value, 1)}")
    # Best/worst movie(s)
    max_rating = max(ratings_list)
    min_rating = min(ratings_list)
    best_movies = []
    worst_movies = []
    for movie, stats in movies_dict.items():
        if stats['rating'] == max_rating:
            best_movies.append(movie)
        elif stats['rating'] == min_rating:
            worst_movies.append(movie)
    # Output all the movies with the worst/best ratings
    if best_movies:
        if len(best_movies) > 1:
            print("Best movies:")
            for best_movie in best_movies:
                print(f"{best_movie} ({movies_dict[best_movie]['year']}), {max_rating}")
        else:
            best_movie_year = movies_dict[best_movies[0]]['year']
            print(f"Best movie: {best_movies[0]} ({best_movie_year}), {max_rating}")

    if worst_movies:
        if len(worst_movies) > 1:
            print("Worst movies:")
            for worst_movie in worst_movies:
                print(f"{worst_movie} ({movies_dict[worst_movie]['year']}), {min_rating}")
        else:
            worst_movie_year = movies_dict[worst_movies[0]]['year']
            print(f"Worst movie: {worst_movies[0]} ({worst_movie_year}), {min_rating}")


def random_movie(movies_dict):
    """
    Get a random number in the length of the dict and count down.
    the printed value is the current loop through the keys, when the nuber hits 0.
    """
    if not movies_dict:
        cprint("No movies to choose from", 'red')
    random_number = random.randint(1, len(movies_dict))
    for movie, stats in movies_dict.items():
        random_number -= 1
        if random_number <= 0:
            cprint("Your movie for tonight:", 'cyan')
            print(f"{movie} ({stats['year']}), it's rated {stats['rating']}")
            break


def search_movie(movies_dict):
    """
    Ask the user for a movie title/part of title.
    if no exact match (case-insensitive) print titles,
    which are close to-/have part of the user search.
    """
    user_search = input(colored("Enter the full title, or part of a movie name: ", 'yellow'))
    correct_search = user_search.title() in movies_dict
    if correct_search:
        print(f"{user_search.title()} ({movies_dict[user_search.title()]['year']})", end=", ")
        print(f"{movies_dict[user_search.title()]['rating']}")
    else:
        cprint(f"No movie with the title '{user_search}' was found!", 'red')
        cprint("\nMaybe you are searching for:", 'cyan')
        found_movies = 0
        for movie, stats in movies_dict.items():
            if _partial_ratio(user_search.lower(), movie.lower()) >= 80:
                print(f"{movie} ({stats['year']}), {stats['rating']}")
                found_movies += 1
        if found_movies <= 0:
            cprint("No movie found", 'red')


def sort_by_rating(movies_dict):
    """Filter out the key with the highest value for each loop on a safe copy"""
    copy_of_dict = movies_dict.copy()
    cprint("The top-bottom ratings are:", 'cyan')
    for loop in range(len(movies_dict)):
        max_key = max(copy_of_dict, key=lambda movie: copy_of_dict[movie]['rating'])
        print(f"{max_key} ({copy_of_dict[max_key]['year']}), {copy_of_dict[max_key]['rating']}")
        del copy_of_dict[max_key]


def create_histogram_from_dict(movies_dict):
    """Create and safe a Histogram in a user-named File"""
    ratings_dict = {}
    for movie, stats in movies_dict.items():
        rating = stats['rating']
        if rating not in ratings_dict:
            ratings_dict[rating] = 0
        ratings_dict[rating] += 1
    plt.bar(list(ratings_dict.keys()), list(ratings_dict.values()))
    plt.title('Ratings of current movies')
    plt.xlabel("Rating (1-10)")
    plt.ylabel("Movies with the same rating")
    safe_file = input(colored("In which file do you want to safe the Histogram? (.png by default):\n", 'yellow'))
    print(f"File '{safe_file}' successfully safed!")
    plt.savefig(safe_file)


# Main Function start
def main():
    """
    Get a movie_dict from the sql database, execute the chosen menu option
    to change the sql table or show stats from the table.
    """
    menu_list = [
        {"name": "Exit",
        "function": quit,},
        {"name": "List movies",
         "function": list_movies},
        {"name": "Add movie",
         "function": add_movie},
        {"name": "Delete movie",
         "function": delete_movie},
        {"name": "Update movie",
         "function": update_movie},
        {"name": "Stats",
         "function": show_stats},
        {"name": "Random movie",
         "function": random_movie},
        {"name": "Search movie",
         "function": search_movie},
        {"name": "Movies sorted by rating",
         "function": sort_by_rating},
        {"name": "Create Rating Histogram",
         "function": create_histogram_from_dict}
    ]
    cprint("\n********** My Movies Database **********\n", 'cyan')

    while True:
        movies = storage.list_movies()
        show_menu(menu_list)
        print()
        try:
            choice_num = int(input(colored(f"Enter choice (0-{len(menu_list) - 1}): ", 'yellow')))
        except ValueError:
            cprint("No number from 0-9 found!", 'red')
            continue
        print()
        if choice_num == 0:
            print("Bye!")
            menu_list[choice_num]['function']()
        menu_list[choice_num]['function'](movies)
        print()
        input(colored("Press enter to continue", 'yellow'))
        print()
        continue


if __name__ == "__main__":
    main()