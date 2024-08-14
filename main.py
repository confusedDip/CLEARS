#!/usr/bin/python3

import os
import sys
from utilities.collab import create_project, add_collaborator, remove_collaborator, share, unshare, end_project
import subprocess

# The path to the source code directory
sys.path.append('/usr/bin/authz')

# A method to check whether 'sudo' is allowed
def is_in_sudoers():
    try:
        # Attempt to execute a command that requires sudo
        subprocess.check_call(['sudo', '-n', 'true'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False
    except PermissionError:
        return False

# The help module: authzmodel help
def print_help():
    print("authzmodel(1)")
    print("\nNAME")
    print("\tauthzmodel - efficiently manage shared privileges")
    print("\nSYNOPSIS")
    print("\tauthzmodel [COMMAND..]")
    print("\nCOMMANDS")
    print("\tstart\tStart a new project. (requires administrative privileges to perform)")
    print("\n\tadd\tAdd collaborators to an existing project. (requires administrative privileges to perform)")
    print("\n\tshare\tShare privileges with a collaborator to access resources within a project.")
    print("\n\tunshare\tRetract previously shared privileges from a collaborator within a project.")
    print("\n\tremove\tRemove collaborators from an existing project. (requires administrative privileges to perform)")
    print("\n\tend\tEnd an existing project. (requires administrative privileges to perform)")
    print("\n\thelp\tLaunch the help menu.")


def main():
    """
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
            Removes a set of collaborators from an existing project
        (8) end_project():
            Ends an existing project
    """

    if len(sys.argv) < 2:
        print("Invalid Input: Please refer `authzmodel help` for documentation")
        return

    action = sys.argv[1].lower()

    accepted_actions = ["start", "add", "remove", "share", "unshare", "end", "help"]

    if action not in accepted_actions:
        print("Invalid Input: Please refer `authzmodel help` for documentation")
        return

    if action == "help":
        print_help()

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
        resource_type = input("Enter the resource type you want to share:\n\t"
                              "Submit 1 for Files/Directories\n\t"
                              "Submit 2 for Computational Partition\n> ")
        resource_to_share = input("Enter the resource name you want to share: ")
        to_users = input("Enter the user names to share with (space separated): ").split()

        share(from_username=from_user, resource_id_to_share=resource_to_share, to_usernames=set(to_users),
              project_id=project_id, resource_type=int(resource_type))

    if action == "unshare":

        from_user = os.getlogin()
        project_id = input("Enter the project name: ")
        resource_type = input("Enter the resource type you want to un-share:\n\t"
                              "Submit 1 for Files/Directories\n\t"
                              "Submit 2 for Computational Partition\n> ")
        resource_to_unshare = input("Enter the resource name you want to un-share: ")

        to_users = input("Enter the user names to un-share with (space separated): ").split()

        unshare(from_username=from_user, resource_id_to_unshare=resource_to_unshare, to_usernames=set(to_users),
                project_id=project_id, resource_type=int(resource_type))

    elif action == "end":
        if is_in_sudoers():
            project_id = input("Enter the project name: ")
            end_project(project_id=project_id)
        else:
            print("end project: This action can only be performed with Administrative Privileges.")


if __name__ == "__main__":
    main()
