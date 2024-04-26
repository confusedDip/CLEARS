class User:

    def __init__(self, uid: str):
        self.uid: str = uid
        self.owned_resources: [str] = []
        add_user(self)

    def get_uid(self) -> str:
        return self.uid

    def add_owner_resource(self, resource):
        self.owned_resources.append(resource)

    def get_owned_resources(self):
        return self.owned_resources


def add_user(user: User):
    if user.uid in Users.users.keys():
        print("User already exists!")
        return
    else:
        Users.users[user.uid] = user
        print(f"User {user.uid} Added!")


def get_user(user_id: str) -> User:
    if user_id in Users.users.keys():
        return Users.users[user_id]


def remove_user(user_id):

    if user_id in Users.users.keys():
        print("No such user exists!")
        return
    else:
        Users.users.pop(user_id)


class Users:
    users = {}
