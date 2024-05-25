import pwd
import subprocess
import time
from collections import deque
from itertools import combinations
# import pygraphviz as pgv
import os
from typing import Tuple

from utilities.resource import get_resource
from utilities.user import remove_project, add_project


def from_dict(data):
    # Convert the list of lists into a list of tuples
    resource_ids = [tuple(item) for item in data["resource_ids"]]
    return Context(
        set(data["user_ids"]),
        set(resource_ids),
        set(data["parents"]),
        set(data["children"])
    )


class Context:

    def __init__(self, user_ids: set[str], resource_ids=None, parents=None, children=None):
        if children is None:
            children = set()
        if resource_ids is None:
            resource_ids = set()
        if parents is None:
            parents = set()
        self.__id: str = ''.join(sorted(user_ids))
        self.__user_ids: set[str] = set(user_ids.copy())
        self.__resource_ids: set[Tuple[int, str]] = resource_ids
        self.__parents: set[str] = parents
        self.__children: set[str] = children

    def to_dict(self):
        return {
            "id": self.__id,
            "user_ids": list(self.__user_ids),
            "resource_ids": list(self.__resource_ids),
            "parents": list(self.__parents),
            "children": list(self.__children)
        }

    def get_id(self) -> str:
        return self.__id

    def get_users(self) -> set[str]:
        return self.__user_ids

    def get_resources(self) -> set[Tuple[int, str]]:
        return self.__resource_ids

    def get_parents(self) -> set[str]:
        return self.__parents

    def add_parents(self, new_parent: str):
        self.__parents.add(new_parent)

    def get_children(self) -> set[str]:
        return self.__children

    def add_children(self, new_child: str):
        self.__children.add(new_child)

    def add_resource(self, resource: str, resource_type: int):
        self.__resource_ids.add((resource_type, resource))

    def remove_resource(self, resource: str, resource_type: int):
        self.__resource_ids.remove((resource_type, resource))

    # def print_context(self) -> str:
    #     context_str = (f"{self.__id}\n" + "{" + ', '.join(sorted(self.__user_ids)) + "}" +
    #                    "\n" "[" + ', '.join(sorted(self.__resource_ids)) + "]")
    #     # print(context_str)
    #     return "{" + ', '.join(sorted(self.__user_ids)) + "}"
    #     return context_str


class Network:

    def __init__(self, user_ids: set[str], project_id: str, root_context=None, contexts=None):

        # Initialize the Network object
        if contexts is None:
            contexts = dict()
        self.__project_id = project_id
        self.__all_user_ids: set[str] = user_ids
        self.__root_context: str = root_context
        self.__contexts: dict[str, Context] = contexts
        # Create the network
        # self.create_network()

    def to_dict(self):
        return {
            "project_id": self.__project_id,
            "all_user_ids": list(self.__all_user_ids),
            "root_context": self.__root_context,
            "contexts": {key: context.to_dict() for key, context in self.__contexts.items()}
        }

    def get_project_id(self) -> str:
        return self.__project_id

    def get_all_user_ids(self) -> set[str]:
        return self.__all_user_ids

    def get_root_context(self) -> str:
        return self.__root_context

    def set_root_context(self, context):
        self.__root_context = context.get_id()

    def add_new_user(self, user: str):
        # Update the set of involved users
        self.__all_user_ids.add(user)
        # Expand the network
        # self.expand_network()
        # Add the project to new user's project list
        # add_project(user_ids=self.__all_user_ids, project_id=self.__project_id, user_id=user)

    def add_context(self, context: Context):

        if context.get_id() not in self.__contexts.keys():
            self.__contexts[context.get_id()] = context

    def get_contexts(self) -> dict[str, Context]:
        return self.__contexts

    def del_context(self, context: Context):

        # print(f"Context to be deleted: {context.get_id()}")
        if context.get_id() in self.__contexts.keys():
            # Remove links from parents
            # for parent_id in context.get_parents():
            #     parent = self.__contexts[parent_id]
            #     parent.get_children().remove(context.get_id())
            #
            # # Remove links from children
            # for child_id in context.get_children():
            #     child = self.__contexts[child_id]
            #     child.get_parents().remove(context.get_id())

            # Delete the context
            del self.__contexts[context.get_id()]

    def expand_network(self):

        new_root_context = Context(self.__all_user_ids)
        self.add_context(new_root_context)
        self.set_root_context(new_root_context)

        # Recursively generate child contexts with one less user until leaf level with two users
        self.generate_child_contexts(new_root_context.get_id(), len(self.__all_user_ids))

    def generate_child_contexts(self, current_context_id: str, num_users: int):

        if num_users <= 2:
            return

        current_context = self.__contexts[current_context_id]

        # Generate child contexts with one less user
        user_combinations = [list(comb)
                             for comb in combinations(current_context.get_users(), num_users - 1)]

        for child_users in user_combinations:

            child_context_id = ''.join(sorted(child_users))
            current_context.add_children(child_context_id)

            if child_context_id in self.__contexts.keys():
                child_context = self.__contexts[child_context_id]

            else:
                child_context = Context(set(child_users))
                self.add_context(child_context)

            child_context.add_parents(current_context_id)

            self.generate_child_contexts(child_context.get_id(), num_users - 1)

    # def print_network(self):
    #
    #     root_context_id = self.__root_context
    #
    #     root_context = self.__contexts[root_context_id]
    #     queue = deque([root_context])
    #     visited = {}
    #
    #     print("Root Context:")
    #     print(root_context.print_context())
    #     visited[root_context.get_id()] = True
    #
    #     print("\nChild Contexts:")
    #
    #     while queue:
    #         current_context = queue.popleft()
    #         for child_context_id in current_context.get_children():
    #             if child_context_id not in visited.keys():
    #                 child_context = self.__contexts[child_context_id]
    #                 print(child_context.print_context())
    #                 queue.append(child_context)
    #                 visited[child_context] = True

    # def visualize_network(self):
    #     g = pgv.AGraph(directed=True)
    #
    #     root_context = self.__root_context
    #     queue = deque([root_context])
    #     visited = {}
    #
    #     while queue:
    #         current_context = queue.popleft()
    #         for child_context in current_context.get_children():
    #             g.add_edge(current_context.print_context(), child_context.print_context())
    #             if child_context not in visited.keys():
    #                 queue.append(child_context)
    #                 visited[child_context] = True
    #
    #     g.layout(prog='dot')
    #     g.draw(f'collaboration_network_{time.time()}.png')
    #     print("Collaboration network visualization saved")

    def share_resource(self, from_user_id: str, resource_id_to_share: str, to_user_ids: set[str], resource_type: int) \
            -> (str, set[str]):

        # Get all users who are involved in the transaction
        involved_users = to_user_ids.union({from_user_id})

        # The purpose is to find whether the resource is already shared within some context
        already_shared_context = None

        for context_id, context in self.__contexts.items():
            resources = context.get_resources()

            # If resource is already shared within the current context
            # Keep a note of the context and remove the resource to elevate later
            # No further search is needed because one resource can be shared at most one context
            if (resource_type, resource_id_to_share) in resources:
                already_shared_context = context
                context.remove_resource(resource_type=resource_type, resource=resource_id_to_share)
                break

        # If the resource is already not shared
        # The context to share is the one with all involved users
        if already_shared_context is None:
            correct_context_id = ''.join(sorted(involved_users))
            if correct_context_id in self.__contexts.keys():
                correct_context = self.__contexts[correct_context_id]
            else:
                correct_context = Context(user_ids=involved_users)
                self.add_context(correct_context)
            correct_users = involved_users

        # If the resource is already shared
        # The context to share is the union on that context and the one with all involved users
        # Privilege Elevation to Super-Collaboration
        else:
            already_shared_users = already_shared_context.get_users()
            correct_users = involved_users.union(already_shared_users)
            correct_context_id = ''.join(sorted(correct_users))
            if correct_context_id in self.__contexts.keys():
                correct_context = self.__contexts[correct_context_id]
            else:
                correct_context = Context(correct_users)
                self.add_context(correct_context)

        correct_context.add_resource(resource=resource_id_to_share, resource_type=resource_type)

        print("Error is not in classes/share_resource()")
        if already_shared_context is None:
            return None, correct_users
        return already_shared_context.get_users(), correct_users

    def unshare_resource(self, from_user_id: str, resource_id_to_unshare: str, to_user_ids: set[str], resource_type: int):

        # Get all users who are involved in the transaction
        involved_users = to_user_ids.union({from_user_id})

        correct_context_id = None  # This is the context where the privileges should be re-shared after un-sharing
        correct_users = set()
        already_shared_context = None

        for context_id, context in self.get_contexts().items():

            users = context.get_users()
            resources = context.get_resources()

            # Only investigate a context if it includes all involved users
            if involved_users.issubset(users):

                # If the context has the shared resources
                # Remove the resource from the current context to the child without
                if (resource_type, resource_id_to_unshare) in resources:

                    context.remove_resource(resource=resource_id_to_unshare, resource_type=resource_type)
                    already_shared_context = context

                    additional_users = users.difference(involved_users)
                    # If the context to unshare is a leaf node (U2U Collaboration), then nothing else to do
                    if len(additional_users) == 0:
                        return already_shared_context.get_users(), None

                    correct_users = additional_users.union({from_user_id})

        correct_context_id = ''.join(sorted(correct_users))

        if correct_context_id in self.__contexts.keys():
            correct_context = self.__contexts[correct_context_id]
        else:
            correct_context = Context(correct_users)
            self.add_context(correct_context)
        correct_context.add_resource(resource=resource_id_to_unshare, resource_type=resource_type)
        return already_shared_context.get_users(), correct_users

    def remove_user(self, user_id: str):

        # Maintain a dict of information to further update privileges
        privileges_to_update = dict()

        # Remove the user from the network object, and remove the project from the user
        self.__all_user_ids.remove(user_id)

        for context_id, context in self.__contexts.copy().items():
            current_context = context

            current_context_users = current_context.get_users()
            current_context_resources = current_context.get_resources().copy()
            other_users = current_context_users - {user_id}

            # Step 1: Check if the user exists in the current context, then it needs to be removed
            if user_id in current_context_users:

                # Step 2: Check if the current context is a leaf context (i.e. U2U collaboration), delete it!
                if len(current_context.get_users()) == 2:

                    for resource_type, resource_path in current_context_resources:
                        privileges_to_update[resource_path] = dict({
                            "already_shared_users": current_context_users,
                            "correct_users": None
                        })

                else:
                    for resource_type, resource_path in current_context_resources:

                        owner_uid = -1

                        # File/Directory
                        if resource_type == 1:
                            resource_metadata = os.stat(resource_path)
                            owner_uid = str(resource_metadata.st_uid)

                        # Computational Partition
                        elif resource_type == 2:
                            # Run the scontrol show partition command and capture the output
                            result = subprocess.run(['scontrol', 'show', 'partition'], stdout=subprocess.PIPE,
                                                    text=True)
                            output = result.stdout.splitlines()

                            for line in output:
                                if line.startswith('PartitionName='):
                                    partition_name = line.split("=")[1]
                                    if partition_name == resource_path:
                                        owner_name = resource_path.split("_")[0]
                                        owner_uid = pwd.getpwnam(owner_name).pw_uid

                        # Step 3: Check if the user have been shared anything within the context, then un-share it
                        # and re-share it with some lower context
                        if owner_uid != user_id:
                            already_shared_users, correct_users = self.unshare_resource(
                                from_user_id=owner_uid,
                                resource_id_to_unshare=resource_path,
                                to_user_ids={user_id},
                                resource_type=resource_type
                            )

                            privileges_to_update[resource_path] = dict({
                                "resource_type": resource_type,
                                "already_shared_users": already_shared_users,
                                "correct_users": correct_users
                            })

                        # Step 4: Check if the user has shared anything within the context, then un-share it
                        else:
                            privileges_to_update[resource_path] = dict({
                                "resource_type": resource_type,
                                "already_shared_users": current_context_users,
                                "correct_users": None
                            })

                # Delete the context from the network
                self.del_context(current_context)

        return privileges_to_update

    def can_access(self, requester_id: str, resource_id: str) -> bool:

        # Obtain the resource from the requested resource_id
        resource = get_resource(resource_id)
        # Obtain the owner uid
        owner_id = resource.get_owner()

        # Use involved_users to find the potential contexts
        involved_users = {owner_id, requester_id}

        # Search across the network to see if the resource has been shared in any of the contexts involving the users
        root_context = self.__root_context
        queue = deque([root_context])
        visited = {}

        # The BFS Loop
        while queue:

            current_context = queue.popleft()
            users = current_context.get_users()

            # If the current context include the two users involved in the request, it needs further investigation
            if involved_users.issubset(users):

                # If the requested resource has been shared here, GRANT access
                resources = current_context.get_resources()
                if resource_id in resources:
                    return True

            for child_context in current_context.get_children():
                if child_context not in visited.keys():
                    queue.append(child_context)
                    visited[child_context] = True

        # If access is not granted by now, DENY
        return False


class Networks:
    networks: [str, Network] = dict()
