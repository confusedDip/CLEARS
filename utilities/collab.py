#!/usr/bin/python3

import grp
import json
import os
import pwd
import subprocess

from classes.collab import Network, from_dict
from ldap.add_user import add_user_to_group
from ldap.connect_ldap import connect_to_ldap
from ldap.create_group import create_group
from ldap.delete_group import delete_group
from ldap.remove_user import remove_user_from_group


def dump_network_to_file(project_file: str, network: Network):
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


def group_exists_and_max_gid(group_name):
    try:
        max_gid = -1
        group_exists = False

        # Run getent group command and capture output
        output = subprocess.check_output(['getent', 'group']).decode('utf-8')
        lines = output.strip().split('\n')

        for line in lines:
            parts = line.split(':')
            if parts[0] == group_name:
                group_exists = True

            # Extract the group ID
            gid = int(parts[2])

            if gid > max_gid and 10000 < gid < 20000:
                max_gid = gid

        return group_exists, max_gid

    except subprocess.CalledProcessError:
        # Handle error if getent group command fails
        return False, -1


def get_file_system(path: str):
    try:
        result = subprocess.run(["stat", "-f", "-c", "%T", path], capture_output=True, text=True, check=True)
        filesystem_type = result.stdout.strip()
        return filesystem_type
    except Exception as e:
        print(f"Error: {e}")


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


def can_share(from_username: str, resource_id: str, to_username: str, project_id: str, resource_type: int) -> bool:
    """
    This is the sharing authorization relation that supports admin defined policies
    :param resource_type: type of the resource (1:file/directory, 2:computational partition)
    :param from_username: which user is requesting to share?
    :param resource_id: what resource (privilege) is concerned?
    :param to_username: to whom is it being shared?
    :param project_id: under which project context the sharing is taking place?
    :return: Allow (True) or Deny (False)
    """

    from_user_id = pwd.getpwnam(from_username).pw_uid
    to_user_id = pwd.getpwnam(to_username).pw_uid

    # Step 0: self-share is not permitted
    if from_user_id == to_user_id:
        print(f"Sharing Error: An attempt to self-share was made!")
        return False

    # Step 0: no to_user mentioned
    if to_username == '':
        print(f"Sharing Error: No recipient mentioned!")
        return False

    # Step 1: Obtain the owner information

    owner_uid = -1  # Initialize a bad owner id
    resource_path = resource_id

    # File/Directory
    if resource_type == 1:
        resource_path = os.path.abspath(resource_id)
        resource_metadata = os.stat(resource_path)
        owner_uid = resource_metadata.st_uid

    # Computational Partition
    elif resource_type == 2:
        # Run the scontrol show partition command and capture the output
        result = subprocess.run(['scontrol', 'show', 'partition'], stdout=subprocess.PIPE, text=True)
        output = result.stdout.splitlines()

        for line in output:
            if line.startswith('PartitionName='):
                partition_name = line.split("=")[1]
                if partition_name.startswith(from_username) and partition_name == resource_id:
                    owner_uid = pwd.getpwnam(from_username).pw_uid

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
                print(f"Sharing Error: The requesting user {from_username} is not the owner of the resource")
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


def share(from_username: str, resource_id_to_share: str, to_usernames: set[str], project_id: str, resource_type: int):
    """
    This is the user action share that first authorizes the action with respect to can_share and then performs the share
    :param resource_type: type of resource (1:file/directory, 2:computational partition)
    :param from_username: which user is requesting to share?
    :param resource_id_to_share: what resource (privilege) is concerned?
    :param to_usernames: to which users is it being shared?
    :param project_id: under which project context the sharing is taking place?
    :return:
    """
    can_share_flag = True
    for to_username in to_usernames.copy():
        if not can_share(from_username, resource_id_to_share, to_username, project_id, resource_type):
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
    wrapper_supdate_path = os.path.join(script_dir, "wrapper_supdate")

    # Set up the LDAP Connection
    conn = connect_to_ldap()

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

        resource_path = resource_id_to_share
        if resource_type == 1:
            resource_path = os.path.abspath(resource_id_to_share)

        # Share and Update the Collaboration Network
        already_shared_users, correct_users = (
            network.share_resource(from_user_id, resource_path, to_user_ids))

        # Now derive the correct collaboration context
        correct_context = project_id + ''.join(sorted(correct_users))

        group_exists, max_gid = group_exists_and_max_gid(group_name=correct_context)

        # Add the new group (collaboration) if it doesn't exist
        if not group_exists:
            create_group(
                conn=conn,
                group_dn=f"cn={correct_context},ou=groups,dc=rc,dc=example,dc=org",
                group_name=correct_context,
                gid_number=max_gid + 1
            )

        # Assign users to the group (collaboration)
        for user_id in correct_users:
            user = pwd.getpwuid(int(user_id))[0]
            add_user_to_group(
                conn=conn,
                group_dn=f"cn={correct_context},ou=groups,dc=rc,dc=example,dc=org",
                user_uid=user
            )

        # Update the privileges accordingly

        # File/Directory
        if resource_type == 1:

            # Revoke rwx access to the group in the ACL of the file
            if already_shared_users is not None:

                already_shared_context = project_id + ''.join(sorted(already_shared_users))

                if get_file_system(resource_path) == "nfs":
                    grp_id = grp.getgrnam(already_shared_context).gr_gid
                    subprocess.run(["nfs4_setfacl", "-x", f"A:g:{grp_id}:rxtcy", resource_path])
                else:
                    subprocess.run(["setfacl", "-x", f"g:{already_shared_context}", resource_path])  # ext

                subprocess.run(["sync"])

                already_shared_unames = set(
                    pwd.getpwuid(int(already_shared_uid))[0] for already_shared_uid in already_shared_users)
                print(f"Collaboration '{already_shared_unames}' removed access to resource '{resource_path}'.")

            # Assign rwx access to the group in the ACL of the file
            if get_file_system(resource_path) == "nfs":
                grp_id = grp.getgrnam(correct_context).gr_gid
                subprocess.run(["nfs4_setfacl", "-a", f"A:g:{grp_id}:RX", resource_path])
            else:
                subprocess.run(["setfacl", "-m", f"g:{correct_context}:rwx", resource_id_to_share])

            subprocess.run(["sync"])

        # Computational Partition
        elif resource_type == 2:

            result = subprocess.run(['scontrol', 'show', 'partition', resource_path],
                                    stdout=subprocess.PIPE, text=True)
            relevant_output = result.stdout.splitlines()[1]  # 'AllowGroups=grp_c AllowAccounts=ALL AllowQos=ALL'
            relevant_config = relevant_output.split()[0]  # 'AllowGroups=grp_c'
            existing_allowed_groups = set(relevant_config.split("=")[1].split(","))  # ('grp_c')

            existing_allowed_groups.add(correct_context)

            # Revoke access to the group
            if already_shared_users is not None:
                already_shared_context = project_id + ''.join(sorted(already_shared_users))
                existing_allowed_groups.remove(already_shared_context)

                already_shared_unames = set(
                    pwd.getpwuid(int(already_shared_uid))[0] for already_shared_uid in already_shared_users)
                print(f"Collaboration '{already_shared_unames}' removed access to resource '{resource_path}'.")

            # Assign access to the group
            correct_new_group = existing_allowed_groups
            new_context = ','.join(correct_new_group)
            subprocess.run([wrapper_supdate_path, resource_path, new_context])

        # Print final Success Message

        correct_unames = set(pwd.getpwuid(int(correct_user))[0] for correct_user in correct_users)
        print(f"Collaboration '{correct_unames}' granted access to resource '{resource_path}'.")

        # Dump the network to the project file
        dump_network_to_file(project_file, network)

    except FileNotFoundError as e:
        print(f"Error: Project {project_id} not found. {e}")

    except Exception as e:
        print(f"Error: {e}")


def can_unshare(from_username: str, resource_id: str, to_username: str, project_id: str, resource_type: int) -> bool:
    """
    This is the un-sharing authorization relation that supports admin defined policies
    :param resource_type: type of the resource (1:file/directory, 2:computational partition)
    :param from_username: which user is requesting to unshare?
    :param resource_id: what resource (privilege) is concerned?
    :param to_username: to whom is it being unshared?
    :param project_id: under which project context the unsharing is taking place?
    :return: Allow (True) or Deny (False)
    """

    from_user_id = pwd.getpwnam(from_username).pw_uid
    to_user_id = pwd.getpwnam(to_username).pw_uid

    # Step 0: self-share is not permitted
    if from_user_id == to_user_id:
        print(f"Un-Sharing Error: An attempt to self-unshare was made!")
        return False

    # Step 0: no to_user mentioned
    if to_username == '':
        print(f"Un-Sharing Error: No recipient mentioned!")
        return False

    # Step 1: Obtain the owner information

    owner_uid = -1  # Initialize a bad owner id
    resource_path = resource_id

    # File/Directory
    if resource_type == 1:
        resource_path = os.path.abspath(resource_id)
        resource_metadata = os.stat(resource_path)
        owner_uid = resource_metadata.st_uid

    # Computational Partition
    elif resource_type == 2:
        # Run the scontrol show partition command and capture the output
        result = subprocess.run(['scontrol', 'show', 'partition'], stdout=subprocess.PIPE, text=True)
        output = result.stdout.splitlines()

        for line in output:
            if line.startswith('PartitionName='):
                partition_name = line.split("=")[1]
                if partition_name.startswith(from_username) and partition_name == resource_id:
                    owner_uid = pwd.getpwnam(from_username).pw_uid

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
                print(f"Un-Sharing Error: The requesting user {from_username} is not the owner of the resource")
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


def unshare(from_username: str, resource_id_to_unshare: str, to_usernames: set[str], project_id: str,
            resource_type: int):
    """
    This is the user action un-share that first authorizes the action with respect to can_unshare and then performs
    the un-share
    :param resource_type: type of the resource (1:file/directory, 2:computational partition)
    :param from_username: which user is requesting to un-share?
    :param resource_id_to_unshare: what resource (privilege) is concerned?
    :param to_usernames: to which users is it being un-shared?
    :param project_id: under which project context the sharing is taking place?
    """

    can_unshare_flag = True
    for to_username in to_usernames.copy():
        if not can_unshare(from_username, resource_id_to_unshare, to_username, project_id, resource_type):
            can_unshare_flag = False

    if not can_unshare_flag:
        print("One of more (from_user, resource, to_user) un-sharing query is not permitted")
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
    wrapper_supdate_path = os.path.join(script_dir, "wrapper_supdate")

    # Set up the ldap connection
    conn = connect_to_ldap()

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

        resource_path = resource_id_to_unshare
        if resource_type == 1:
            resource_path = os.path.abspath(resource_id_to_unshare)

        # Unshare and Update the Collaboration Network
        already_shared_users, correct_users = (
            network.unshare_resource(from_user_id, resource_path, to_user_ids))

        # Construct the collaboration already enjoying the privileges and remove privileges
        already_shared_context = project_id + ''.join(sorted(already_shared_users))

        # File/Directory
        if resource_type == 1:

            if get_file_system(resource_path) == "nfs":
                grp_id = grp.getgrnam(already_shared_context).gr_gid
                subprocess.run(["nfs4_setfacl", "-x", f"A:g:{grp_id}:rxtcy", resource_path])
            else:
                subprocess.run(["setfacl", "-x", f"g:{already_shared_context}", resource_path])  # ext

            subprocess.run(["sync"])

        # Computational Partition
        elif resource_type == 2:

            result = subprocess.run(['scontrol', 'show', 'partition', resource_path],
                                    stdout=subprocess.PIPE, text=True)
            relevant_output = result.stdout.splitlines()[1]  # 'AllowGroups=grp_c AllowAccounts=ALL AllowQos=ALL'
            relevant_config = relevant_output.split()[0]  # 'AllowGroups=grp_c'
            existing_allowed_groups = set(relevant_config.split("=")[1].split(","))  # ('grp_c')

            existing_allowed_groups.remove(already_shared_context)

            # Revoke the privileges
            correct_new_group = existing_allowed_groups
            new_context = ','.join(correct_new_group)
            subprocess.run([wrapper_supdate_path, resource_path, new_context])

        # Print the message of un-sharing the privileges
        already_shared_unames = set(
            pwd.getpwuid(int(already_shared_uid))[0] for already_shared_uid in already_shared_users)
        print(f"Collaboration '{already_shared_unames}' removed access to resource '{resource_path}'.")

        # Now perform the privilge-contraction and re-share privileges
        if correct_users is not None:
            # Now assign to the correct context
            correct_context = project_id + ''.join(sorted(correct_users))

            group_exists, max_gid = group_exists_and_max_gid(group_name=correct_context)

            # Add the new group if it doesn't exist
            if not group_exists:
                # subprocess.run([wrapper_groupadd_path, correct_context])
                create_group(
                    conn=conn,
                    group_dn=f"cn={correct_context},ou=groups,dc=rc,dc=example,dc=org",
                    group_name=correct_context,
                    gid_number=max_gid + 1
                )

            # Assign users to the group
            for user_id in correct_users:
                user = pwd.getpwuid(int(user_id))[0]
                add_user_to_group(
                    conn=conn,
                    group_dn=f"cn={correct_context},ou=groups,dc=rc,dc=example,dc=org",
                    user_uid=user
                )

            # File/Directory
            if resource_type == 1:

                # Assign rwx access to the group in the ACL of the file
                if get_file_system(resource_path) == "nfs":
                    grp_id = grp.getgrnam(correct_context).gr_gid
                    subprocess.run(["nfs4_setfacl", "-m", f"A:g:{grp_id}:RX", resource_path])
                else:
                    subprocess.run(["setfacl", "-m", f"g:{correct_context}:rwx", resource_path])

                subprocess.run(["sync"])

            # Computational Partition
            elif resource_type == 2:

                # Assign access to the group
                correct_new_group = existing_allowed_groups
                correct_new_group.add(correct_context)
                new_context = ','.join(correct_new_group)
                subprocess.run([wrapper_supdate_path, resource_path, new_context])

            # Finally print the sharing message
            correct_unames = set(
                pwd.getpwuid(int(correct_uid))[0] for correct_uid in correct_users)
            print(f"Collaboration '{correct_unames}' granted access to resource '{resource_path}'.")

        # Dump the network to the project file
        dump_network_to_file(project_file, network)

    except FileNotFoundError:
        print(f"Error: Project {project_id} not found.")

    except Exception as e:
        print(f"Error: {e}")


def remove_collaborator(project_id: str, users: set[str]):
    """
    It is an administrative action to remove collaborators to a project
    :param project_id: The unique identifier to refer to the project
    :param users: List of user ids that are to be removed from the project
    """
    # Define the base directory
    base_dir = "/etc/project"

    # Create the full path for the project
    project_file = os.path.join(base_dir, project_id) + ".json"

    # Get the directory path of the currently executing Python script
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Construct the full path to the c wrappers
    wrapper_groupadd_path = os.path.join(script_dir, "wrapper_groupadd")
    wrapper_usermod_path = os.path.join(script_dir, "wrapper_usermod")

    # Setup the LDAP connection
    conn = connect_to_ldap()

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

        groups_to_delete = set()
        user_groups_to_remove = set()

        for username in users:
            user_id = pwd.getpwnam(username).pw_uid
            privileges_to_update = network.remove_user(user_id=str(user_id))
            print(f"{username}(uid={user_id}) successfully removed from {project_id}")

            for resource_path, item in privileges_to_update.items():
                already_shared_users = item["already_shared_users"]
                correct_users = item["correct_users"]

                if already_shared_users is not None:
                    # Remove rwx access to the group in the ACL of the file
                    already_shared_context = project_id + ''.join(sorted(already_shared_users))

                    if get_file_system(resource_path) == "nfs":
                        grp_id = grp.getgrnam(already_shared_context).gr_gid
                        subprocess.run(["sudo", "nfs4_setfacl", "-x", f"A:g:{grp_id}:rxtcy", resource_path])
                    else:
                        subprocess.run(["sudo", "setfacl", "-x", f"g:{already_shared_context}", resource_path])

                    subprocess.run(["sync"])

                    # Remove the users from the group
                    for user_id in already_shared_users:
                        user = pwd.getpwuid(int(user_id))[0]
                        user_groups_to_remove.add((user_id, already_shared_context))
                        groups_to_delete.add(already_shared_context)

                    # Sync Changes
                    subprocess.run(["sync"])

                    already_shared_unames = set(
                        pwd.getpwuid(int(already_shared_uid))[0] for already_shared_uid in already_shared_users)
                    print(f"Collaboration '{already_shared_unames}' removed access to file '{resource_path}'.")

                if correct_users is not None:
                    # Now assign to the correct context
                    correct_context = project_id + ''.join(sorted(correct_users))

                    # with open("/var/lib/extrausers/group", "r") as file:
                    # with open("/etc/group", "r") as file:
                    #     existing_groups = file.read().splitlines()
                    #     group_exists = any(
                    #         group_info.split(':')[0] == correct_context for group_info in existing_groups)
                    #
                    # # Add the new group if it doesn't exist
                    # if not group_exists:
                    #     subprocess.run([wrapper_groupadd_path, correct_context])
                    #
                    # # Assign users to the group
                    # for user_id in correct_users:
                    #     user = pwd.getpwuid(int(user_id))[0]
                    #     subprocess.run([wrapper_usermod_path, correct_context, user])

                    group_exists, max_gid = group_exists_and_max_gid(group_name=correct_context)

                    # Add the new group if it doesn't exist
                    if not group_exists:
                        create_group(
                            conn=conn,
                            group_dn=f"cn={correct_context},ou=groups,dc=rc,dc=example,dc=org",
                            group_name=correct_context,
                            gid_number=max_gid + 1
                        )

                    # Assign users to the group
                    for user_id in correct_users:
                        user = pwd.getpwuid(int(user_id))[0]
                        add_user_to_group(
                            conn=conn,
                            group_dn=f"cn={correct_context},ou=groups,dc=rc,dc=example,dc=org",
                            user_uid=user
                        )

                    # Assign rwx access to the group in the ACL of the file

                    if get_file_system(resource_path) == "nfs":
                        grp_id = grp.getgrnam(correct_context).gr_gid
                        subprocess.run(["sudo", "nfs4_setfacl", "-m", f"A:g:{grp_id}:RX", resource_path])
                    else:
                        subprocess.run(["sudo", "setfacl", "-m", f"g:{correct_context}:rwx", resource_path])

                    subprocess.run(["sync"])

                    correct_unames = set(
                        pwd.getpwuid(int(correct_uid))[0] for correct_uid in correct_users)
                    print(f"Collaboration '{correct_unames}' granted access to file '{resource_path}'.")

        # Remove the user-group associations
        for user, group in user_groups_to_remove:
            # subprocess.run(["sudo", "deluser", user, group])
            remove_user_from_group(
                conn=conn,
                group_dn=f"cn={group},ou=groups,dc=rc,dc=example,dc=org",
                user_uid=user
            )

        # Delete the groups
        for group in groups_to_delete:
            # subprocess.run(["sudo", "groupdel", group])
            delete_group(conn=conn, group_dn=f"cn={group},ou=groups,dc=rc,dc=example,dc=org")

        dump_network_to_file(project_file, network)

    except FileNotFoundError:
        print(f"Error: Project {project_id} not found.")
    except Exception as e:
        print(f"Error: {e}")


def end_project(project_id: str):
    """
    It is an administrative action to end a project
    :param project_id: The unique identifier to refer to the project
    """

    # Define the base directory
    base_dir = "/etc/project"

    # Create the full path for the project
    project_file = os.path.join(base_dir, project_id) + ".json"

    try:
        # Read all lines from the project file
        with open(project_file, "r") as file:
            data = json.load(file)
            user_ids = set(data['all_user_ids'])
            usernames = [pwd.getpwuid(int(user_id))[0] for (user_id) in user_ids]
            remove_collaborator(project_id=project_id, users=set(usernames))

        # os.remove(project_file)
        print(f"Project {project_id} ended successfully!")

    except FileNotFoundError:
        print(f"Error: Project {project_id} not found.")
    except Exception as e:
        print(f"Error: {e}")

# def can_access(requester_id: str, resource_id: str) -> bool:
#     print(f"Requester: {requester_id}, Requested Resource: {resource_id}")
#
#     # Obtain the resource from the requested resource_id
#     resource = get_resource(resource_id)
#     # Obtain the owner uid
#     owner_id = resource.get_owner()
#
#     # Always allow the owner to access
#     if requester_id == owner_id:
#         return True
#
#     # Obtain the mutual projects of the owner and the requestor
#     owner_projects = get_user(owner_id).get_projects()
#     requester_projects = get_user(requester_id).get_projects()
#     mutual_projects = owner_projects.intersection(requester_projects)
#
#     # If they do not work on any common project, deny!
#     if len(mutual_projects) == 0:
#         return False
#
#     # Explore the collaboration network for each project to make a decision
#     for project in mutual_projects:
#         network = get_network(project)
#         print(f"Checking the Collaboration Network for Project {project}")
#         if network.can_access(requester_id, resource_id):
#             return True
#         else:
#             print("False!")
#
#     return False
