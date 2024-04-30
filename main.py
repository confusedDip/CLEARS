from classes.resource import Resource
from classes.user import User, get_user
from classes.collab import Network, get_network, can_access


def main():
    # Create four users: A, B, C, D
    User("A")
    User("B")
    User("C")
    User("D")

    # Give the users some resources to own
    for uid in {"A", "B", "C", "D"}:
        user = get_user(user_id=uid)
        for i in range(1, 5):
            r = Resource(rid=f"{uid}{i}", owner=user)
            user.add_owned_resource(r)

    # Start a project P1 with A, B, C
    Network(user_ids={"A", "B", "C"}, project_id="P1")
    # Start a project P2 with A, D
    Network(user_ids={"A", "D"}, project_id="P2")

    # Obtain the network for project P1
    network_p1 = get_network("P1")
    network_p1.visualize_network()

    # Invite D to the project P1
    network_p1.add_new_user("D")
    network_p1.visualize_network()

    network_p1.share_resource("A", "A1", {"B", "C", "D"})
    network_p1.visualize_network()

    network_p1.share_resource("A", "A2", {"B", "C", "D"})
    network_p1.visualize_network()

    network_p1.share_resource("A", "A3", {"B", "C"})
    network_p1.visualize_network()

    network_p1.unshare_resource("A", "A1", {"B", "C"})
    network_p1.visualize_network()

    network_p1.unshare_resource("A", "A2", {"B"})
    network_p1.visualize_network()

    network_p1.share_resource("A", "A3", {"B"})
    network_p1.visualize_network()

    network_p1.share_resource("D", "D1", {"A", "B"})
    network_p1.visualize_network()

    print(can_access("A", "A2"))  # True
    print(can_access("B", "A2"))  # False
    print(can_access("C", "A2"))  # True
    print(can_access("A", "B1"))  # False
    print(can_access("D", "A2"))  # True

    network_p1.remove_user("D")

    network_p1.visualize_network()

    print(can_access("D", "A2"))  # False
    print(can_access("D", "A2"))  # False
    print(can_access("A", "D1"))  # False


if __name__ == "__main__":
    main()
