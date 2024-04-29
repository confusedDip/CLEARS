from classes.resource import Resource
from classes.user import User, Users
from classes.collab import Network


def main():
    User("A")
    User("B")
    User("C")

    network = Network(set(Users.users.keys()))
    network.visualize_network()

    User("D")
    network.add_new_user("D")

    for uid, user in Users.users.items():
        for i in range(1, 5):
            r = Resource(rid=f"{uid}{i}", owner=user)
            user.add_owner_resource(r)

    network.visualize_network()

    network.share_resource("A", "A1", {"B", "C", "D"})
    network.visualize_network()

    network.share_resource("A", "A2", {"B", "C", "D"})
    network.visualize_network()

    network.share_resource("A", "A3", {"B", "C"})
    network.visualize_network()

    network.unshare_resource("A", "A1", {"B", "C"})
    network.visualize_network()

    network.unshare_resource("A", "A2", {"B"})
    network.visualize_network()

    network.share_resource("A", "A3", {"B"})
    network.visualize_network()

    network.share_resource("D", "D1", {"A", "B"})
    network.visualize_network()

    print(network.can_access("A", "A2"))  # True
    print(network.can_access("B", "A2"))  # False
    print(network.can_access("C", "A2"))  # True
    print(network.can_access("A", "B1"))  # False
    print(network.can_access("D", "A2"))  # True

    network.remove_user("D")

    network.visualize_network()

    print(network.can_access("D", "A2"))  # False
    print(network.can_access("D", "A2"))  # False
    print(network.can_access("A", "D1"))  # False


if __name__ == "__main__":
    main()
