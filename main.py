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
            user.addOwnerResource(r)

    network = Network(list(Users.users.keys()))

    network.share_resource("A", "A_1", {"B", "C"})
    network.share_resource("A", "A_2", {"B", "C"})
    network.unshare_resource("A", "A_2", {"B"})
    network.share_resource("A", "A_3", {"B", "C"})
    network.share_resource("A", "A_4", {"B"})
    network.share_resource("B", "B_1", {"C"})

    User("D")
    network.add_new_user("D")

    network.share_resource("A", "A_1", {"D"})


if __name__ == "__main__":
    main()
