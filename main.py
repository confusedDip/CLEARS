from classes.resource import Resource
from classes.user import User, Users
from classes.collab import Network

def main():
    
    User("A")
    User("B")
    User("C")

    for uid, user in Users.users.items():
        for i in range(1, 5):
            r = Resource(rid = f"{uid}{i}", owner = user)
            user.addOwnerResource(r)

    network = Network(list(Users.users.keys()))
    network.visualize_network()

    User("D")
    network.add_new_user("D")
    network.visualize_network()
    


if __name__ == "__main__":
    main()