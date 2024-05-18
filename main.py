#!/usr/bin/python3

import os
import sys

sys.path.append('/usr/local/bin/authz')

from utilities.collab import can_access, create_project, add_collaborator, remove_collaborator, can_share, can_unshare, \
    share, unshare, end_project
from utilities.user import create_user, get_user
from utilities.resource import create_resource
import subprocess


def is_in_sudoers():
    try:
        # Attempt to execute a command that requires sudo
        subprocess.check_call(['sudo', '-n', 'ls'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    """
    Here I will update the progress:

        (1) create_project():
            Takes a project id and registers the project in the system
        (2) add_collaborator():
            Adds set of collaborators to an existing project
        (3) can_share():
            Takes from and to user ids and resource local path, and the project id to authorize the sharing
        (4) share():
            Authorizes via can_share(), then performs the share()
        (5) can_unshare():
            Takes from and to user ids and resource local path, and the project id to authorize the un-sharing
        (6) unshare():
            Authorizes via can_unshare(), then performs the unshare()
        (7) remove_collaborator():

        (8) end_project():
    """

    args = sys.argv
    user = os.getlogin()

    if len(sys.argv) < 2:
        print("Invalid Input: Please refer `./main.py help` for documentation")
        return

    if len(sys.argv) == 2 and sys.argv[1].lower() == "help":
        # print_help()
        return

    action = sys.argv[1].lower()

    accepted_actions = ["start", "add", "remove", "share", "unshare", "end"]

    if action not in accepted_actions:
        print("Invalid Input: Please refer `./main.py help` for documentation")
        return

    if action == "start":

        if is_in_sudoers():
            project_id = input("Enter the project name: ")
            create_project(project_id=project_id)
        else:
            print("start project: This action can only be performed with Administrative Privileges.")

    elif action == "add":

        if is_in_sudoers():
            project_id = input("Enter the project name: ")
            collaborators = input("Enter the user names to add (space separated): ").split()
            add_collaborator(project_id, set(collaborators))
        else:
            print("add collaborators: This action can only be performed with Administrative Privileges.")

    if action == "remove":
        if is_in_sudoers():
            project_id = input("Enter the project name: ")
            collaborators = input("Enter the user names to remove (space separated): ").split()
            remove_collaborator(project_id, set(collaborators))
        else:
            print("remove collaborators: This action can only be performed with Administrative Privileges.")

    elif action == "share":

        from_user = os.getlogin()
        project_id = input("Enter the project name: ")
        resource_to_share = input("Enter the resource name you want to share: ")
        to_users = input("Enter the user names to share with (space separated): ").split()

        share(from_username=from_user, resource_id_to_share=resource_to_share, to_usernames=set(to_users),
              project_id=project_id)

    if action == "unshare":

        from_user = os.getlogin()
        project_id = input("Enter the project name: ")
        resource_to_unshare = input("Enter the resource name you want to un-share: ")
        to_users = input("Enter the user names to un-share with (space separated): ").split()

        unshare(from_username=from_user, resource_id_to_unshare=resource_to_unshare, to_usernames=set(to_users),
                project_id=project_id)

    elif action == "end":
        if is_in_sudoers():
            project_id = input("Enter the project name: ")
            end_project(project_id=project_id)
        else:
            print("end project: This action can only be performed with Administrative Privileges.")

    # create_project(project_id="P2")
    #
    # add_collaborator(project_id="P2", users={"pwn_dp", "bailey", "cathy"})
    #
    # # can_share(from_username="pwn_dp", resource_id="data.json", to_username="bailey", project_id="P2")
    # # can_share(from_username="pwn_dp", resource_id="data2.json", to_username="cathy", project_id="P2")
    # # can_share(from_username="bailey", resource_id="data2.json", to_username="cathy", project_id="P2")
    # # can_share(from_username="pwn_dp", resource_id="data2.json", to_username="sefcom", project_id="P2")
    #
    # share(project_id="P2", from_username="pwn_dp", resource_id_to_share="data.json", to_usernames={"bailey", "cathy"})
    # add_collaborator(project_id="P2", users={"sefcom"})
    # share(project_id="P2", from_username="pwn_dp", resource_id_to_share="data.json", to_usernames={"sefcom"})
    #
    # # can_unshare(from_username="pwn_dp", resource_id="data.json", to_username="bailey", project_id="P2")
    # # can_unshare(from_username="pwn_dp", resource_id="data2.json", to_username="cathy", project_id="P2")
    # # can_unshare(from_username="bailey", resource_id="data2.json", to_username="cathy", project_id="P2")
    # # can_unshare(from_username="pwn_dp", resource_id="data2.json", to_username="sefcom", project_id="P2")
    # # can_unshare(from_username="pwn_dp", resource_id="data.json", to_username="sefcom", project_id="P2")
    #
    # share(project_id="P2", from_username="pwn_dp", resource_id_to_share="data2.json", to_usernames={"bailey",
    # "sefcom"})
    # unshare(project_id="P2", from_username="pwn_dp", resource_id_to_unshare="data.json", to_usernames={
    # "cathy"}) unshare(project_id="P2", from_username="pwn_dp", resource_id_to_unshare="data.json", to_usernames={
    # "bailey"})

    # t = 2: Alex invites collaborator Bailey and Cathy
    # invite_collaborator(user_id=creator, project_id="P1", users={"Bailey"})
    # invite_collaborator(user_id=creator, project_id="P1", users={"Cathy"})

    # t = 3: Alex shares resource Alex_1 with Bailey and Cathy
    # share_privilege(project_id="P1", from_user_id=creator, resource_id_to_share="/home/pwn_dp/papers.txt",
    #                 to_user_ids={"Bailey"})
    # share_privilege(project_id="P1", from_user_id=creator, resource_id_to_share="/home/pwn_dp/papers.txt",
    #                 to_user_ids={"Cathy"})

    # t = 4: Alex shares resources Alex_2 Alex_3 with Bailey and Cathy
    # share_privilege(project_id="P1", from_user_id=creator, resource_id_to_share="/home/pwn_dp/references.txt",
    #                 to_user_ids={"Bailey", "Cathy"})
    # share_privilege(project_id="P1", from_user_id=creator, resource_id_to_share="/home/pwn_dp/data.json",
    #                 to_user_ids={"Bailey", "Cathy"})

    # t = 5: Alex shares Alex_4 only with Bailey
    # share_privilege(project_id="P1", from_user_id=creator, resource_id_to_share="/home/pwn_dp/data2.json",
    #                 to_user_ids={"Bailey"})
    #
    # # t = 6: Bailey shares Bailey_1 only with Cathy
    # share_privilege(project_id="P1", from_user_id="Bailey", resource_id_to_share="/home/pwn_dp/bailey_results.json",
    #                 to_user_ids={"Cathy"})

    # t = 7: Alex invites collaborator Drew
    # invite_collaborator(user_id=creator, project_id="P1", users={"Drew"})

    # t = 8: Alex shares Alex_3 with Drew (Example of Privilege Elevation)
    # share_privilege(project_id="P1", from_user_id=creator, resource_id_to_share="/home/pwn_dp/data.json",
    #                 to_user_ids={"Drew"})

    # t = 9: Bailey shares Bailey_1 with Drew (Example of Privilege Elevation)
    # share_privilege(project_id="P1", from_user_id="Bailey", resource_id_to_share="/home/pwn_dp/bailey_results.json",
    #                 to_user_ids={"Drew"})

    # t = 10: Alex un-shares Alex_3 with Drew (Example of Privilege Descent)
    # unshare_privilege(project_id="P1", from_user_id=creator, resource_id_to_unshare="/home/pwn_dp/data.json",
    #                   to_user_ids={"Drew"})

    # t = 11: Alex removes Drew from the project


if __name__ == "__main__":
    main()
