from classes.resource import Resource
from classes.user import User, Users
from classes.collab import Network


def main():
    User("A")
    User("B")
    User("C")

    for uid, user in Users.users.items():
        for i in range(1, 5):
            r = Resource(rid=f"{uid}{i}", owner=user)
            user.add_owner_resource(r)

    network = Network(set(Users.users.keys()))

    network.share_resource("A", "A1", {"B", "C"})
    network.share_resource("A", "A2", {"B", "C"})
    network.unshare_resource("A", "A2", {"B"})
    network.share_resource("A", "A3", {"B", "C"})
    network.share_resource("A", "A4", {"B"})
    network.share_resource("B", "B1", {"C"})

    User("D")
    network.add_new_user("D")

    network.share_resource("A", "A1", {"D"})

    print(network.can_access("A", "A2"))    # True
    print(network.can_access("B", "A2"))    # False
    print(network.can_access("C", "A2"))    # True
    print(network.can_access("A", "B1"))    # False
    print(network.can_access("D", "A2"))    # False


if __name__ == "__main__":
    main()
