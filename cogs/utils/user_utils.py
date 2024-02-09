import json
import os


FILEPATH = "/home/ec2-user/frostnova/cogs/_data/users.json"

def get_users():
    '''Reads the entire JSON file containing users' data and returns it as a Python dictionary object.'''
    with open(FILEPATH, "r") as json_data:
        users_dict = json.load(json_data)
    return users_dict


def update(user_dict):
    '''Updates the entire JSON file containing users' data with the given Python dictionary object.'''
    with open(FILEPATH, "w") as json_out:
        json.dump(user_dict, json_out, indent=4)


def is_registered(user):
    '''Returns true if the user's user_id is a key in the user dictionary, false otherwise.'''
    return str(user.id) in list(get_users().keys())


def get_default_keys():
    '''Initializes a set of default key-value pairs that each user will be assigned when registering for the first time.'''
    return {
        "balance": 1000,
        "slot_winnings": 0
    }


def get_balance(user):
    '''Returns a user's balance.'''
    return get_users()[str(user.id)]["balance"]


def set_balance(user, balance):
    '''Sets a user's balance to the specified amount. This function assumes that the user is properly registered in the dictionary of
    registered users. Attempting to set the user's balance to a negative number will set it to 0 instead.'''
    if balance < 0:
        balance = 0
    user_dict = get_users()
    user_dict[str(user.id)]["balance"] = balance
    update(user_dict)
    
    
def add_balance(user, balance):
    '''Adds a specified amount to the user's balance. This function assumes that the user is properly registered in the dictionary of
    registered users.'''
    user_dict = get_users()
    user_dict[str(user.id)]["balance"] = user_dict[str(user.id)]["balance"] + balance 
    update(user_dict)


def get_slot_winnings(user):
    '''Returns a user's lifetime slot winnings.'''
    return get_users()[str(user.id)]["slot_winnings"]
