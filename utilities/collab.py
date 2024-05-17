#!/usr/bin/python3

import json

from classes.collab import Network, Networks, from_dict
from utilities.user import get_user, add_project, remove_project
from utilities.resource import get_resource
import os, pwd
import subprocess


def dump_network_to_file(project_file: str, network: Network):
    # try:
    #     # Create the project directory
    #     with open(project_file, "w") as file:
    #         json.dump(network.to_dict(), file, indent=4)
    #     print(f"Project '{network.get_project_id()}' created/updated successfully.")
    #
    # except FileExistsError:
    #     print(f"Project '{network.get_project_id()}' already exists.")
    # except OSError as e:
    #     print(f"Failed to create project '{network.get_project_id()}': {e}")
    # Serialize the network to a JSON string

    network_json = json.dumps(network.to_dict(), indent=4)

    # Get the directory path of the currently executing Python script
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Construct the full path to the C wrapper
    wrapper_script_path = os.path.join(script_dir, "wrapper_network_dump")

    # Check if the wrapper script exists
    if not os.path.exists(wrapper_script_path):
        raise FileNotFoundError(f"Wrapper script '{wrapper_script_path}' not found.")

    try:
        # Call the C wrapper with the project file and network JSON
        result = subprocess.run([wrapper_script_path, project_file, network_json],
                                check=True, text=True, capture_output=True)
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"Failed to create project '{network.get_project_id()}': {e.stderr}")



def create_project(project_id: str):
    """
    It is an administrative action to initiate a project
    This initializes the corresponding project file within /etc/project directory
    Also, initializes an empty collaboration network object
    :param project_id: An unique identifier for the project
    """
    # Model Tasks:
    network = Network(user_ids=set(), project_id=project_id)

    # OS Tasks:

    # Define the base directory
    base_dir = "/etc/project"

    # Create the full path for the project
    project_file = os.path.join(base_dir, project_id) + ".json"

    # Dump the network to the project file
    dump_network_to_file(project_file, network)


def add_collaborator(project_id: str, users: set[str]):
    """
    It is an administrative action to add collaborators to a project
    :param project_id: The unique identifier to refer to the project
    :param users: List of user ids that are to be added to the project
    """
    # Define the base directory
    base_dir = "/etc/project"

    # Create the full path for the project
    project_file = os.path.join(base_dir, project_id) + ".json"

    try:
        # Read all lines from the project file
        with open(project_file, "r") as file:
            data = json.load(file)
            network = Network(
                user_ids=set(data['all_user_ids']),
                project_id=data['project_id'],
                root_context=data['root_context'],
                contexts={key: from_dict(context_data) for key, context_data in data["contexts"].items()}
            )

        for new_username in users:
            new_user_id = pwd.getpwnam(new_username).pw_uid
            network.add_new_user(user=str(new_user_id))
            print(f"{new_username}(uid={new_user_id}) successfully added to {project_id}")

        dump_network_to_file(project_file, network)

    except FileNotFoundError:
        print("Error: Project not found.")
    except Exception as e:
        print(f"Error: {e}")


def can_share(from_username: str, resource_id: str, to_username: str, project_id: str) -> bool:
    """
    This is the sharing authorization relation that supports admin defined policies
    :param from_username: which user is requesting to share?
    :param resource_id: what resource (privilege) is concerned?
    :param to_username: to whom is it being shared?
    :param project_id: under which project context the sharing is taking place?
    :return: Allow (True) or Deny (False)
    """

    from_user_id = pwd.getpwnam(from_username).pw_uid
    to_user_id = pwd.getpwnam(to_username).pw_uid

    # Step 1: Obtain the owner information
    resource_path = os.path.abspath(resource_id)
    resource_metadata = os.stat(resource_path)
    owner_uid = resource_metadata.st_uid
    owner_name = pwd.getpwuid(owner_uid)[0]

    # Step 2: Obtain the user list of the project
    # Define the base directory
    base_dir = "/etc/project"

    # Create the full path for the project
    project_file = os.path.join(base_dir, project_id) + ".json"

    try:
        # Read all lines from the project file
        with open(project_file, "r") as file:
            data = json.load(file)

            collaborators = data['all_user_ids']

            # Check for the two constraints
            if owner_uid != from_user_id:
                print(f"Sharing Error: The requesting user {owner_name} is not the owner of the resource")
                return False
            else:
                if (str(from_user_id) not in collaborators) or (str(to_user_id) not in collaborators):
                    print(f"Sharing Error: {from_username} and {to_username} are not collaborators within {project_id}")
                    return False
                else:
                    print(f"Sharing {resource_path} Allowed: From {from_username} to {to_username}")
                    return True

    except FileNotFoundError:
        print(f"Sharing Error: Project {project_id} not found.")
        return False
    except Exception as e:
        print(f"Sharing Error: {e}")
        return False


def share(from_username: str, resource_id_to_share: str, to_usernames: set[str], project_id: str, ):
    """
    This is the user action share that first authorizes the action with respect to can_share and then performs the share
    :param from_username: which user is requesting to share?
    :param resource_id_to_share: what resource (privilege) is concerned?
    :param to_usernames: to which users is it being shared?
    :param project_id: under which project context the sharing is taking place?
    :return:
    """
    can_share_flag = True
    for to_username in to_usernames.copy():
        if not can_share(from_username, resource_id_to_share, to_username, project_id):
            can_share_flag = False

    if not can_share_flag:
        print("One of more (from_user, resource, to_user) sharing query is not permitted")
        return

    # Define the base directory
    base_dir = "/etc/project"

    # Create the full path for the project
    project_file = os.path.join(base_dir, project_id) + ".json"

    # Get the directory path of the currently executing Python script
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Construct the full path to the c wrappers
    wrapper_groupadd_path = os.path.join(script_dir, "wrapper_groupadd")
    wrapper_usermod_path = os.path.join(script_dir, "wrapper_usermod")

    try:
        # Read all lines from the project file
        with open(project_file, "r") as file:
            data = json.load(file)
            network = Network(
                user_ids=set(data['all_user_ids']),
                project_id=data['project_id'],
                root_context=data['root_context'],
                contexts={key: from_dict(context_data) for key, context_data in data["contexts"].items()}
            )

        from_user_id = str(pwd.getpwnam(from_username).pw_uid)
        to_user_ids = set(str(pwd.getpwnam(to_username).pw_uid) for to_username in to_usernames)
        resource_path = os.path.abspath(resource_id_to_share)

        already_shared_users, correct_users = (
            network.share_resource(from_user_id, resource_path, to_user_ids))

        if already_shared_users is not None:
            # Remove rwx access to the group in the ACL of the file
            already_shared_context = project_id + ''.join(sorted(already_shared_users))
            subprocess.run(["setfacl", "-x", f"g:{already_shared_context}", resource_path])

            already_shared_unames = set(
                pwd.getpwuid(int(already_shared_uid))[0] for already_shared_uid in already_shared_users)
            print(f"Collaboration '{already_shared_unames}' removed rwx access to file '{resource_path}'.")

        # Now assign to the correct context
        correct_context = project_id + ''.join(sorted(correct_users))

        with open("/etc/group", "r") as file:
            existing_groups = file.read().splitlines()
            group_exists = any(group_info.split(':')[0] == correct_context for group_info in existing_groups)

        # Add the new group if it doesn't exist
        if not group_exists:
            subprocess.run([wrapper_groupadd_path, correct_context])

        # Assign users to the group
        for user_id in correct_users:
            user = pwd.getpwuid(int(user_id))[0]
            subprocess.run([wrapper_usermod_path, correct_context, user], check=True)

        # Assign rwx access to the group in the ACL of the file
        subprocess.run(["setfacl", "-m", f"g:{correct_context}:rwx", resource_id_to_share])

        correct_unames = set(pwd.getpwuid(int(correct_user))[0] for correct_user in correct_users)
        print(f"Collaboration '{correct_unames}' granted rwx access to file '{resource_path}'.")

        # Dump the network to the project file
        dump_network_to_file(project_file, network)

    except FileNotFoundError as e:
        print(f"Error: Project {project_id} not found. {e}")

    except Exception as e:
        print(f"Error: {e}")


def can_unshare(from_username: str, resource_id: str, to_username: str, project_id: str) -> bool:
    """
    This is the un-sharing authorization relation that supports admin defined policies
    :param from_username: which user is requesting to unshare?
    :param resource_id: what resource (privilege) is concerned?
    :param to_username: to whom is it being unshared?
    :param project_id: under which project context the unsharing is taking place?
    :return: Allow (True) or Deny (False)
    """

    from_user_id = pwd.getpwnam(from_username).pw_uid
    to_user_id = pwd.getpwnam(to_username).pw_uid

    # Step 1: Obtain the owner information
    resource_path = os.path.abspath(resource_id)
    resource_metadata = os.stat(resource_path)
    owner_uid = resource_metadata.st_uid
    owner_name = pwd.getpwuid(owner_uid)[0]

    # Step 2: Obtain the user list of the project
    # Define the base directory
    base_dir = "/etc/project"

    # Create the full path for the project
    project_file = os.path.join(base_dir, project_id) + ".json"

    try:
        # Read all lines from the project file
        with open(project_file, "r") as file:
            data = json.load(file)
            network = Network(
                user_ids=set(data['all_user_ids']),
                project_id=data['project_id'],
                root_context=data['root_context'],
                contexts={key: from_dict(context_data) for key, context_data in data["contexts"].items()}
            )

            collaborators = data['all_user_ids']

            # Check for the two constraints
            if owner_uid != from_user_id:
                print(f"Un-Sharing Error: The requesting user {owner_name} is not the owner of the resource")
                return False
            else:
                if (str(from_user_id) not in collaborators) or (str(to_user_id) not in collaborators):
                    print(
                        f"Un-Sharing Error: {from_username} and {to_username} are not collaborators within {project_id}")
                    return False
                else:
                    # Check if the privilege has been previously shared or not!
                    for context_id, context in network.get_contexts().items():
                        collaborators = context.get_users()
                        if str(to_user_id) in collaborators and str(from_user_id) in collaborators:
                            resources = context.get_resources()
                            if resource_path in resources:
                                print(f"Un-Sharing {resource_path} Allowed: From {from_username} to {to_username}")
                                return True

                    print(f"Un-Sharing Error: {resource_path} was never shared with {to_username} within {project_id}")
                    return False

    except FileNotFoundError:
        print(f"Un-Sharing Error: Project {project_id} not found.")
        return False
    except Exception as e:
        print(f"Un-Sharing Error: {e}")
        return False


def unshare(from_username: str, resource_id_to_unshare: str, to_usernames: set[str], project_id: str):
    """
    This is the user action un-share that first authorizes the action with respect to can_unshare and then performs
    the un-share
    :param from_username: which user is requesting to un-share?
    :param resource_id_to_unshare: what resource (privilege) is concerned?
    :param to_usernames: to which users is it being un-shared?
    :param project_id: under which project context the sharing is taking place?
    """

    can_unshare_flag = True
    for to_username in to_usernames.copy():
        if not can_unshare(from_username, resource_id_to_unshare, to_username, project_id):
            can_unshare_flag = False

    if not can_unshare_flag:
        print("One of more (from_user, resource, to_user) un-sharing query is not permitted")
        return

    # Define the base directory
    base_dir = "/etc/project"

    # Create the full path for the project
    project_file = os.path.join(base_dir, project_id) + ".json"

    try:
        # Read all lines from the project file
        with open(project_file, "r") as file:
            data = json.load(file)
            network = Network(
                user_ids=set(data['all_user_ids']),
                project_id=data['project_id'],
                root_context=data['root_context'],
                contexts={key: from_dict(context_data) for key, context_data in data["contexts"].items()}
            )

        from_user_id = str(pwd.getpwnam(from_username).pw_uid)
        to_user_ids = set(str(pwd.getpwnam(to_username).pw_uid) for to_username in to_usernames)
        resource_path = os.path.abspath(resource_id_to_unshare)

        already_shared_users, correct_users = (
            network.unshare_resource(from_user_id, resource_path, to_user_ids))

        if already_shared_users is not None:
            # Remove rwx access to the group in the ACL of the file
            already_shared_context = project_id + ''.join(sorted(already_shared_users))
            subprocess.run(["sudo", "setfacl", "-x", f"g:{already_shared_context}", resource_path])
            already_shared_unames = set(
                pwd.getpwuid(int(already_shared_uid))[0] for already_shared_uid in already_shared_users)
            print(f"Collaboration '{already_shared_unames}' removed rwx access to file '{resource_path}'.")

        if correct_users is not None:
            # Now assign to the correct context
            correct_context = project_id + ''.join(sorted(correct_users))

            with open("/etc/group", "r") as file:
                existing_groups = file.read().splitlines()
                group_exists = any(group_info.split(':')[0] == correct_context for group_info in existing_groups)

            # Add the new group if it doesn't exist
            if not group_exists:
                subprocess.run(["sudo", "groupadd", correct_context])

            # Assign users to the group
            for user_id in correct_users:
                user = pwd.getpwuid(int(user_id))[0]
                subprocess.run(["sudo", "usermod", "-aG", correct_context, user])

            # Assign rwx access to the group in the ACL of the file
            subprocess.run(["sudo", "setfacl", "-m", f"g:{correct_context}:rwx", resource_path])
            correct_unames = set(
                pwd.getpwuid(int(correct_uid))[0] for correct_uid in correct_users)
            print(f"Collaboration '{correct_unames}' granted rwx access to file '{resource_path}'.")

        # Dump the network to the project file
        dump_network_to_file(project_file, network)

    except FileNotFoundError:
        print(f"Error: Project {project_id} not found.")

    except Exception as e:
        print(f"Error: {e}")


def can_access(requester_id: str, resource_id: str) -> bool:
    print(f"Requester: {requester_id}, Requested Resource: {resource_id}")

    # Obtain the resource from the requested resource_id
    resource = get_resource(resource_id)
    # Obtain the owner uid
    owner_id = resource.get_owner()

    # Always allow the owner to access
    if requester_id == owner_id:
        return True

    # Obtain the mutual projects of the owner and the requestor
    owner_projects = get_user(owner_id).get_projects()
    requester_projects = get_user(requester_id).get_projects()
    mutual_projects = owner_projects.intersection(requester_projects)

    # If they do not work on any common project, deny!
    if len(mutual_projects) == 0:
        return False

    # Explore the collaboration network for each project to make a decision
    for project in mutual_projects:
        network = get_network(project)
        print(f"Checking the Collaboration Network for Project {project}")
        if network.can_access(requester_id, resource_id):
            return True
        else:
            print("False!")

    return False


def end_project(project_id: str):
    #TODO
    # network = get_network(project_id)
    # # Remove the network from the set of networks
    # remove_network(network)
    # # Remove the project to each user's project list
    # remove_project(user_ids=network.get_all_user_ids(), project_id=network.get_project_id())
    # # Delete the project
    # del network

    project_file_path = "/etc/project"

    # Flag to indicate if the project ID was found
    project_found = False

    try:
        # Read all lines from the project file
        with open(project_file_path, "r") as file:
            lines = file.readlines()

        # Open the project file in write mode to update it
        with open(project_file_path, "w") as file:
            # Check each line in the file
            for line in lines:
                # Check if the line starts with the project ID
                if line.startswith(f"{project_id}:"):
                    # Project ID found, set the flag
                    project_found = True
                else:
                    # Write the line back to the file (excluding the project to be ended)
                    file.write(line)

        # Check if the project ID was found
        if project_found:
            print(f"Project '{project_id}' ended successfully.")
        else:
            print(f"Error: Project ID '{project_id}' not found.")

    except FileNotFoundError:
        print("Error: Project file not found.")
    except Exception as e:
        print(f"Error: {e}")
