from cogs.utils.bot_utils import Item
import json
import os


FILEPATH = "/home/ec2-user/frostnova/cogs/_data/users.json"

def get_users():
    """Reads the entire JSON file containing users' data and returns it as a Python dictionary object."""
    with open(FILEPATH, "r") as json_data:
        users_dict = json.load(json_data)
    return users_dict


def get_user(user):
    """Reads a specific user's data from the JSON file and returns it as a Python dictionary object."""
    with open(FILEPATH, "r") as json_data:
        users_dict = json.load(json_data)
    return users_dict[str(user.id)]


def update(user_dict):
    """Updates the entire JSON file containing users' data with the given Python dictionary object."""
    with open(FILEPATH, "w") as json_out:
        json.dump(user_dict, json_out, indent=4)


def is_registered(user):
    """Returns true if the user's user_id is a key in the user dictionary, false otherwise."""
    return str(user.id) in list(get_users().keys())


def get_default_keys():
    """Initializes a set of default key-value pairs that each user will be assigned when registering for the first time."""
    return {
        "balance": 1000,
        "inventory": {},
        "completion_count": {}
    }


def get_balance(user):
    """Returns a user's balance."""
    return get_user(user)["balance"]


def can_afford(user, amount):
    """Returns true if the amount specified is less than or equal to the user's balance, false otherwise."""
    return amount <= get_balance(user)


def set_balance(user, balance):
    """Sets a user's balance to the specified amount. This function assumes that the user is properly registered in the dictionary of
    registered users. Attempting to set the user's balance to a negative number will set it to 0 instead."""
    if balance < 0:
        balance = 0
    user_dict = get_users()
    user_dict[str(user.id)]["balance"] = balance
    update(user_dict)
    
    
def add_balance(user, balance):
    """Adds a specified amount to the user's balance. This function assumes that the user is properly registered in the dictionary of
    registered users."""
    user_dict = get_users()
    user_dict[str(user.id)]["balance"] = user_dict[str(user.id)]["balance"] + balance 
    update(user_dict)


def get_inventory(user):
    """Fetches the user's inventory, delimited by line breaks."""
    inventory = get_user(user)["inventory"]
    items = []
    for item in inventory:
        items.append(f"{inventory[item]['icon']} {item}×{inventory[item]['quantity']:,}")
    return "\n".join(items)


def add_item(user, item: Item, quantity: int=1):
    """Adds an item to the specified user's inventory. The Item object is deconstructed into a Python dictionary object here to prevent
    issues from reading and writing the user JSON file downstream. Can optionally specify the quantity, but defaults to 1."""
    user_dict = get_users()
    inventory = user_dict[str(user.id)]["inventory"]
    if not inventory or item.name not in inventory.keys():
        inventory[item.name] = {"icon": item.icon, "quantity": quantity}
    else:
        new_quantity = inventory[item.name]["quantity"] + quantity
        inventory[item.name]["quantity"] = new_quantity
    user_dict[str(user.id)]["inventory"] = inventory
    update(user_dict)


def increment_completion_count(user, key: str):
    """Increments the given completion count key by 1, then returns the new completion count value."""
    user_dict = get_users()
    if key not in user_dict[str(user.id)]["completion_count"].keys():
        user_dict[str(user.id)]["completion_count"][key] = 1
    else:
        user_dict[str(user.id)]["completion_count"][key] = user_dict[str(user.id)]["completion_count"][key] + 1
    update(user_dict)
    return user_dict[str(user.id)]["completion_count"][key]
