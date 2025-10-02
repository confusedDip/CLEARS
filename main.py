#!/usr/bin/python3

import os
import sys
from utilities.collab import create_project, add_collaborator, remove_collaborator, share, unshare, end_project
import subprocess
import argparse

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
    parser = argparse.ArgumentParser(description='Authorization Model CLI')
    parser.add_argument('action', choices=["start", "add", "remove", "share", "unshare", "end", "help"],
                        help='Action to perform')
    parser.add_argument('--mode', choices=['interactive', 'non-interactive'], default='interactive',
                        help='Mode of operation')
    parser.add_argument('-p', '--project', help='Project ID')
    parser.add_argument('-o', '--owner', help='Owner / Command Initiator')
    parser.add_argument('-u', '--users', nargs='*', help='Usernames (space-separated list)')
    parser.add_argument('-r', '--resource', help='Resource name to share/unshare')
    parser.add_argument('-t', '--type', type=int, choices=[1, 2], help='Resource type (1 for file, 2 for compute)')

    args = parser.parse_args()
    action = args.action.lower()

    if action == "help":
        print_help()
        return


    if args.mode == "interactive":
        """
        The default mode to be used by real stakeholders
        when in production, interactive
        """
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

        elif action == "remove":
            if is_in_sudoers():
                project_id = input("Enter the project name: ")
                collaborators = input("Enter the user names to remove (space separated): ").split()
                remove_collaborator(project_id, set(collaborators))
            else:
                print("remove collaborators: This action can only be performed with Administrative Privileges.")

        elif action == "share":
            from_user = os.getlogin()
            project_id = input("Enter the project name: ")
            resource_type = int(input("Enter the resource type (1=file, 2=compute): "))
            resource_name = input("Enter the resource name: ")
            users = input("Enter usernames to share with: ").split()
            share(from_username=from_user, resource_id_to_share=resource_name, to_usernames=set(users),
                  project_id=project_id, resource_type=resource_type)

        elif action == "unshare":
            from_user = os.getlogin()
            project_id = input("Enter the project name: ")
            resource_type = int(input("Enter the resource type (1=file, 2=compute): "))
            resource_name = input("Enter the resource name: ")
            users = input("Enter usernames to unshare with: ").split()
            unshare(from_username=from_user, resource_id_to_unshare=resource_name, to_usernames=set(users),
                    project_id=project_id, resource_type=resource_type)

        elif action == "end":
            if is_in_sudoers():
                project_id = input("Enter the project name: ")
                end_project(project_id=project_id)
            else:
                print("end project: This action can only be performed with Administrative Privileges.")


    elif args.mode == "non-interactive":
        """
        The test mode to be used only for evaluation, non-interactive
        """
        project_id = args.project
        users = set(args.users) if args.users else set()
        resource = args.resource
        resource_type = args.type
        from_user = args.owner

        # if action in ["start", "add", "remove", "end"] and not is_in_sudoers():
        #     print(f"{action} requires administrative privileges.")
        #     return

        if action == "start":
            create_project(project_id=project_id)
        elif action == "add":
            add_collaborator(project_id, users)
        elif action == "remove":
            remove_collaborator(project_id, users)
        elif action == "end":
            end_project(project_id=project_id)
        elif action == "share":
            share(from_username=from_user, resource_id_to_share=resource,
                  to_usernames=users, project_id=project_id, resource_type=resource_type)
        elif action == "unshare":
            unshare(from_username=from_user, resource_id_to_unshare=resource,
                    to_usernames=users, project_id=project_id, resource_type=resource_type)


if __name__ == "__main__":
    main()
