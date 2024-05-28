import time
from collections import deque
from itertools import combinations
import pygraphviz as pgv

from archive.classes.resource import get_resource
from archive.classes.user import remove_project, add_project


class Context:

    def __init__(self, user_ids: set[str]):
        self.__id: str = ''.join(sorted(user_ids))
        self.__user_ids: set[str] = set(user_ids.copy())
        self.__resource_ids: set[str] = set()
        self.__parents: set[Context] = set()
        self.__children: set[Context] = set()

    def get_id(self) -> str:
        return self.__id

    def get_users(self) -> set[str]:
        return self.__user_ids

    def get_resources(self) -> set[str]:
        return self.__resource_ids

    def get_parents(self):
        return self.__parents

    def get_children(self):
        return self.__children

    def add_resource(self, resource: str):
        self.__resource_ids.add(resource)

    def remove_resource(self, resource: str):
        self.__resource_ids.remove(resource)

    def print_context(self) -> str:
        context_str = (f"{self.__id}\n" + "{" + ', '.join(sorted(self.__user_ids)) + "}" +
                       "\n" "[" + ', '.join(sorted(self.__resource_ids)) + "]")
        # print(context_str)
        return context_str


class Network:

    def __init__(self, user_ids: set[str], project_id: str):

        # Initialize the Network object
        self.__project_id = project_id
        self.__all_user_ids: set[str] = user_ids
        self.__root_context: Context | None = None
        self.__contexts: dict[str, Context] = {}
        # Create the network
        self.create_network()

    def get_project_id(self) -> str:
        return self.__project_id

    def get_all_user_ids(self) -> set[str]:
        return self.__all_user_ids

    def get_root_context(self) -> Context | None:
        return self.__root_context

    def set_root_context(self, context):
        self.__root_context = context

    def add_new_user(self, user: str):
        # Update the set of involved users
        self.__all_user_ids.add(user)
        # Expand the network
        self.expand_network()
        # Add the project to new user's project list
        add_project(user_ids=self.__all_user_ids, project_id=self.__project_id, user_id=user)

    def add_context(self, context: Context):

        if context.get_id() not in self.__contexts.keys():
            self.__contexts[context.get_id()] = context

    def del_context(self, context: Context):

        print(f"Context to be deleted: {context.get_id()}")
        if context.get_id() in self.__contexts.keys():

            # Remove links from parents
            for parent in context.get_parents():
                parent.get_children().remove(context)

            # Remove links from children
            for child in context.get_children():
                child.get_parents().remove(context)

            # Delete the context
            del self.__contexts[context.get_id()]

    def create_network(self):

        root_context = Context(self.__all_user_ids)
        self.add_context(root_context)
        self.set_root_context(root_context)

        # Recursively generate child contexts with one less user until leaf level with two users
        self.generate_child_contexts(root_context, len(self.__all_user_ids))

    def expand_network(self):

        new_root_context = Context(self.__all_user_ids)
        self.add_context(new_root_context)
        self.set_root_context(new_root_context)

        # Recursively generate child contexts with one less user until leaf level with two users
        self.generate_child_contexts(new_root_context, len(self.__all_user_ids))

    def generate_child_contexts(self, parent_context: Context, num_users: int):

        if num_users <= 2:
            return

        # Generate child contexts with one less user
        user_combinations = [list(comb) for comb in combinations(parent_context.get_users(), num_users - 1)]

        for child_users in user_combinations:

            child_context_id = ''.join(sorted(child_users))

            if child_context_id in self.__contexts.keys():
                child_context = self.__contexts[child_context_id]

            else:
                child_context = Context(set(child_users))
                self.add_context(child_context)

            parent_context.get_children().add(child_context)
            child_context.get_parents().add(parent_context)

            self.generate_child_contexts(child_context, num_users - 1)

    def print_network(self):

        root_context = self.__root_context

        queue = deque([root_context])
        visited = {}

        print("Root Context:")
        print(root_context.print_context())
        visited[root_context.get_id()] = True

        print("\nChild Contexts:")

        while queue:
            current_context = queue.popleft()
            for child_context in current_context.get_children():
                if child_context not in visited.keys():
                    print(child_context.print_context())
                    queue.append(child_context)
                    visited[child_context] = True

    def visualize_network(self):
        g = pgv.AGraph(directed=True)

        root_context = self.__root_context
        queue = deque([root_context])
        visited = {}

        while queue:
            current_context = queue.popleft()
            for child_context in current_context.get_children():
                g.add_edge(current_context.print_context(), child_context.print_context())
                if child_context not in visited.keys():
                    queue.append(child_context)
                    visited[child_context] = True

        g.layout(prog='dot')
        g.draw(f'collaboration_network_{time.time()}.png')
        print("Collaboration network visualization saved")

    def share_resource(self, from_user_id: str, resource_id_to_share: str, to_user_ids: set[str]):

        # Allow only the owner to share
        resource_to_share = get_resource(resource_id=resource_id_to_share)

        if from_user_id != resource_to_share.get_owner():
            print(f"Error: Only owner of a resource can share it!")
            return

        # Get all users who are involved in the transaction
        involved_users = to_user_ids.union({from_user_id})

        # Start with the root context and do a Breadth-First-Search (BFS)
        root_context = self.__root_context
        queue = deque([root_context])
        visited = {}

        # The purpose is to find whether the resource is already shared within some context
        already_shared_context = None

        # The BFS Loop
        while queue:
            current_context = queue.popleft()

            resources = current_context.get_resources()

            # If resource is already shared within the current context
            # Keep a note of the context and remove the resource to elevate later
            # No further search is needed because one resource can be shared at most one context
            if resource_id_to_share in resources:

                already_shared_context = current_context
                current_context.remove_resource(resource_id_to_share)
                break

            # If resource is not shared within the current context
            # Continue the search
            else:

                for child_context in current_context.get_children():

                    # Prune the subtrees where the sharer is not present
                    if from_user_id in child_context.get_users():
                        if child_context not in visited.keys():
                            queue.append(child_context)
                            visited[child_context] = True

        # If the resource is already not shared
        # The context to share is the one with all involved users
        if already_shared_context is None:
            correct_context = ''.join(sorted(involved_users))

        # If the resource is already shared
        # The context to share is the union on that context and the one with all involved users
        # Privilege Elevation to Super-Collaboration
        else:
            already_shared_users = already_shared_context.get_users()
            correct_users = involved_users.union(already_shared_users)
            correct_context = ''.join(sorted(correct_users))

        self.__contexts[correct_context].add_resource(resource_id_to_share)
        print(f"Correct Context: {correct_context}")

        # self.visualize_network()

    def unshare_resource(self, from_user_id: str, resource_id_to_unshare: str, to_user_ids: set[str],
                         root_context=None):

        # Get all users who are involved in the transaction
        involved_users = to_user_ids.union({from_user_id})

        # Start with the root context and do a Breadth-First-Search (BFS)

        if root_context is None:
            root_context = self.__root_context
        queue = deque([root_context])
        visited = {}

        correct_context_id = ''  # This is the context where the privileges should be re-shared after un-sharing

        # The purpose is to find which context the resources are shared
        # The BFS Loop
        while queue:
            current_context = queue.popleft()

            if current_context.get_id() == correct_context_id:
                current_context.add_resource(resource_id_to_unshare)
                print(f"Resource {resource_id_to_unshare} is re-shared in {current_context.get_id()}")
                return

            users = current_context.get_users()
            resources = current_context.get_resources()

            # Only investigate a context if it includes all involved users
            if involved_users.issubset(users):

                # If the context has the shared resources
                # Remove the resource from the current context to the child without
                if resource_id_to_unshare in resources:

                    current_context.remove_resource(resource_id_to_unshare)
                    print(f"Resource {resource_id_to_unshare} is unshared from {current_context.get_id()}")

                    additional_users = users.difference(involved_users)
                    print(f"Additional Users: {additional_users}")
                    # If the context to unshare is a leaf node, then nothing else to do
                    if len(additional_users) == 0:
                        # self.visualize_network()
                        return

                    correct_users = additional_users.union({from_user_id})
                    correct_context_id = ''.join(sorted(correct_users))

            for child_context in current_context.get_children():
                if child_context not in visited.keys():
                    queue.append(child_context)
                    visited[child_context] = True

    def remove_user(self, user_id: str):

        # Remove the user from the network object, and remove the project from the user
        self.__all_user_ids.remove(user_id)
        remove_project(self.__all_user_ids, self.__project_id, user_id)

        # Start with the root context and do a Breadth-First-Search (BFS)
        root_context = self.__root_context
        stack = deque([root_context])

        visited = {}

        # The purpose is to find which all contexts involve the user and need to be removed
        # The DFS Loop
        while stack:

            current_context = stack[-1]

            if current_context.get_id() in visited.keys():
                stack.pop()
                self.del_context(current_context)
                continue
            else:
                visited[current_context.get_id()] = True

            users = current_context.get_users()
            resources = current_context.get_resources().copy()
            other_users = users - {user_id}

            # Step 1: Check if the user exists in the current context, then it needs to be removed
            if user_id in users:

                # Step 2: Check if the current context is a leaf context, delete it!
                if len(current_context.get_children()) == 0:
                    stack.pop()
                    self.del_context(current_context)
                    continue

                for resource_id in resources:

                    # Step 3: Check if the user have been shared anything within the context, then unshare it
                    if get_resource(resource_id).get_owner() != user_id:
                        self.unshare_resource(
                            from_user_id=get_resource(resource_id).get_owner(),
                            resource_id_to_unshare=resource_id,
                            to_user_ids={user_id},
                            root_context=current_context
                        )

                # Step 4: Check if the current context is the root context, then update the root
                # And push all children except the updated root
                if current_context == self.__root_context:

                    new_root_context_id = ''.join(sorted(other_users))
                    for child_context in current_context.get_children():
                        if child_context.get_id() == new_root_context_id:
                            self.__root_context = child_context
                        else:
                            stack.append(child_context)

                # Otherwise, push all children to the stack
                else:
                    for child_context in current_context.get_children():
                        if child_context.get_id() not in visited.keys():
                            stack.append(child_context)

            else:
                stack.pop()

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
