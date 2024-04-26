class User:

    def __init__(self, uid):
        self.uid = uid
        self.owned_resources = []
        Users.add_user(self)

    def getUID(self):
        return self.uid
    
    def addOwnerResource(self, resource):
        self.owned_resources.append(resource)
    
    def getOwnedResources(self):
        return self.owned_resources

class Users:

    users = {}

    def add_user(user):
        
        if user.uid in Users.users.keys():
            print("User already exists!")
            return
        else:
            Users.users[user.uid] = user
            print(f"User {user.uid} Added!")

    def remove_user(Users, user_id):

        if user_id in Users.users.keys():
            print("No such user exists!")
            return 
        else:
            Users.users.pop(user_id)
