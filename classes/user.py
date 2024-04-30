class User:

    def __init__(self, uid: str):
        self.__uid: str = uid
        self.__projects: set[str] = set()
        self.__owned_resources: set[str] = set()
        add_user(self)

    def get_uid(self) -> str:
        return self.__uid

    def add_owned_resource(self, resource):
        self.__owned_resources.add(resource)

    def get_owned_resources(self) -> [str]:
        return self.__owned_resources

    def add_project(self, project_id: str):
        if project_id not in self.__projects:
            self.__projects.add(project_id)

    def remove_project(self, project_id: str):
        if project_id in self.__projects:
            self.__projects.remove(project_id)

    def get_projects(self) -> set[str]:
        return self.__projects


def add_user(user: User):
    if user.get_uid() in Users.users.keys():
        print("User already exists!")
        return
    else:
        Users.users[user.get_uid()] = user
        print(f"User {user.get_uid()} Added!")


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
