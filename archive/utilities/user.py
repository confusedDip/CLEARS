from archive.classes.user import User, Users


def create_user(user_id: str):
    user = User(uid=user_id)
    add_user(user)


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


def add_project(user_ids: set[str], project_id: str, user_id=None):
    if user_id is not None:
        user = get_user(user_id=user_id)
        user.add_project(project_id)
        print(f"Project {project_id} is added to User {user_id}")
        return

    for user_id in user_ids:
        user = get_user(user_id)
        user.add_project(project_id)
        print(f"Project {project_id} is added to User {user_id}")


def remove_project(user_ids: set[str], project_id: str, user_id=None):
    if user_id is not None:
        user = get_user(user_id=user_id)
        user.remove_project(project_id)
        print(f"Project {project_id} is removed from User {user_id}")
        return

    for user_id in user_ids:
        user = get_user(user_id)
        user.remove_project(project_id)
        print(f"Project {project_id} is removed from User {user_id}")
