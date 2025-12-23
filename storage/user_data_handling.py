from sqlalchemy import create_engine, text
from termcolor import cprint, colored
import storage.movie_storage_sql as storage


DB_URL = "sqlite:///../data/users.db"

engine = create_engine(DB_URL)

# Create the movies table if it does not exist
with engine.connect() as connection:
    connection.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL
        );
    """))


def user_menu():
    """
    Fetch the data from the users.db
    display users and create-user as menu.
    if a change on the user is wanted, return "change_users"
    to start the menu_action function.
    return: {user_id: user_name}, chosen via number.
        OR: "change_users" if the highest menu number was chosen.
    """
    with engine.connect() as connection:
        result = connection.execute(text("SELECT user_id, user_name FROM users;"))
        user_data = result.fetchall()
        user_list = [row[1] for row in user_data]
        user_ids = [row[0] for row in user_data]
    counter = 0
    cprint("\nSelect a user:", 'cyan')
    for user in user_list:
        cprint(f"{counter}- {user}", 'green')
        counter += 1
    cprint(f"{counter}- Create, update or delete user", 'green')
    counter += 1
    cprint(f"{counter}- Exit menu", 'green')
    print()
    # Get choice_num from the menu, break if the last choice was made
    while True:
        try:
            choice_num = int(input(colored(f"Please enter a menu choice: (0-{len(user_list)+1}): ", 'yellow')))
            if 0 <= choice_num <= len(user_list) + 1:
                if choice_num == len(user_list):
                    return "change_users"
                elif choice_num == len(user_list) + 1:
                    return "back"
                return {user_ids[choice_num]: user_list[choice_num]}
        except ValueError:
            cprint("Please enter a number from the menu!", 'red')


def get_user_id():
    """
    Ask the user for a user_id from the database and return it, if valid.
    Returns: {user_id(int): user_name(str)}
    """
    with engine.connect() as connection:
        result = connection.execute(text("SELECT user_id, user_name FROM users;"))
        user_data = result.fetchall()
        user_ids = [row[0] for row in user_data]
        user_list = [row[1] for row in user_data]
        print(user_ids)
        print(user_list)
    # Display users and id's ask the user for an id and new_name, until valid input is made.
    while True:
        cprint("\nUsers and id's: ", 'cyan')
        counter = 0
        for user in user_list:
            cprint(f"{user_ids[counter]}- {user}", 'green')
            counter += 1
        # Get a valid user_id
        while True:
            try:
                id_to_update = int(input(colored("\nSelect a user_id to change: ", 'yellow')))
                if id_to_update in user_ids:
                    return id_to_update
                else:
                    raise ValueError
            except ValueError:
                cprint("No valid id!", 'red')


def delete_user():
    """Delete a user from the database."""
    user_id = get_user_id()
    with engine.connect() as connection:
        try:
            connection.execute(text("DELETE FROM users WHERE user_id = :id"),
                               {"id": user_id})
            connection.commit()
            cprint("User deleted successfully", 'green')
        except Exception as e:
            cprint(f"Error: {e}", "red")


def update_user():
    """Ask the user for a user's name in the database to update the name of it."""
    user_id = get_user_id()
    new_name = ""
    while not new_name:
        new_name = input(colored("Please enter a new user name: ", 'yellow'))
        break
    else:
        cprint("Id doesn't exist!\n", 'red')
    # Update the user_name with the chosen id
    with engine.connect() as connection:
        try:
            connection.execute(text("UPDATE users SET user_name = :new_name WHERE user_id = :user_id"),
                               {"new_name": new_name, "user_id": user_id})
            connection.commit()
            cprint("User updated successfully", 'green')
        except Exception as e:
            cprint(f"Error: {e}", "red")


def add_user():
    """ Add a user to the database, Create a new movie database with user_id"""
    new_user = ""
    while not new_user:
        new_user = input(colored("\nPlease enter a new user name: ", 'yellow'))
    with engine.connect() as connection:
        connection.execute(text("INSERT INTO users (user_name) VALUES (:user_name);"),
                            {"user_name": new_user})
        connection.commit()
        result = connection.execute(text("SELECT user_id from users WHERE user_name = :user_name;"),
                                    {"user_name": new_user})
        rows = result.fetchall()
    storage.create_table(rows[0][0])
    cprint("User added successfully", 'green')


def option_menu(menu_dict):
    """
    Display menu from a dictionary with functions.
    add an extra choice to go back from the menu.
    ask the user for a menu choice_num and return it, once validated.

    Returns: (choice_num(int), choice_name(str))
    """
    cprint("\nOptions:", 'cyan')
    for option, function in sorted(menu_dict.items()):
        cprint(f"{option}- {function['name']}", 'green')
    cprint(f"{len(menu_dict)}- Go Back", 'green')
    while True:
        try:
            choice_num = int(input(colored(f"Enter a choice from the menu: (0-{len(menu_dict)}): ", 'yellow')))
            if 0 <= choice_num <= len(menu_dict):
                return choice_num
            else:
                raise ValueError
        except ValueError:
            cprint("Please enter a number from the menu!", 'red')


# Main function loop
def menu_action():
    """
    Display a menu of users and a CRUD option
    based on the user_choice use a function on the users.db
    Or display the CRUD menu.
    return a user_id for the main program to use, if a user was chosen.

    Returns: {user_id(int): user_name(str)}
    """
    menu_functions = {0: {"name": "Exit",
                          "function":  quit},
                      1: {"name": "Add user",
                          "function": add_user},
                      2: {"name": "Update user",
                          "function": update_user},
                      3: {"name": "Delete user",
                          "function": delete_user}
                      }
    while True:
        menu_choice = user_menu()
        if menu_choice == "change_users":
            choice_num = option_menu(menu_functions)
            if choice_num == len(menu_functions):
                continue
            menu_functions[choice_num]["function"]()
        elif menu_choice == "back":
            print("\n\n")
            break
        else:
            return menu_choice


menu_action()