import datetime
from collections import deque
from itertools import combinations
import pygraphviz as pgv

from classes.resource import get_resource


class Context:

    def __init__(self, user_ids: set[str]):
        self.id: str = ''.join(sorted(user_ids))
        self.user_ids: set[str] = set(user_ids.copy())
        self.resource_ids: set[str] = set()
        self.parents: set[Context] = set()
        self.children: set[Context] = set()

    def get_users(self) -> set[str]:
        return self.user_ids

    def get_resources(self) -> set[str]:
        return self.resource_ids

    def add_resource(self, resource: str):
        self.resource_ids.add(resource)

    def remove_resource(self, resource: str):
        self.resource_ids.remove(resource)

    def print_context(self) -> str:
        context_str = (f"{self.id}\n" + "{" + ', '.join(list(self.user_ids)) + "}" +
                       "\n" "[" + ', '.join(list(self.resource_ids)) + "]")
        # print(context_str)
        return context_str


class Network:

    def __init__(self, user_ids: set[str]):
        self.all_user_ids: set[str] = user_ids
        self.root_context: Context | None = None
        self.contexts: dict[str, Context] = {}
        self.create_network()

    def add_new_user(self, user: str):
        self.all_user_ids.add(user)
        self.expand_network()

    def add_context(self, context: Context):

        if context.id not in self.contexts.keys():
            self.contexts[context.id] = context

    def create_network(self):

        root_context = Context(self.all_user_ids)
        self.add_context(root_context)
        self.root_context = root_context

        # Recursively generate child contexts with one less user until leaf level with two users
        self.generate_child_contexts(root_context, len(self.all_user_ids))

    def expand_network(self):

        new_root_context = Context(self.all_user_ids)
        self.add_context(new_root_context)
        self.root_context = new_root_context

        # Recursively generate child contexts with one less user until leaf level with two users
        self.generate_child_contexts(new_root_context, len(self.all_user_ids))

    def generate_child_contexts(self, parent_context: Context, num_users: int):

        if num_users <= 2:
            return

        # Generate child contexts with one less user
        user_combinations = [list(comb) for comb in combinations(parent_context.user_ids, num_users - 1)]

        for child_users in user_combinations:

            child_context_id = ''.join(sorted(child_users))

            if child_context_id in self.contexts.keys():
                child_context = self.contexts[child_context_id]

            else:
                child_context = Context(set(child_users))
                self.add_context(child_context)

            parent_context.children.add(child_context)
            child_context.parents.add(parent_context)

            self.generate_child_contexts(child_context, num_users - 1)

    def print_network(self):

        root_context = self.root_context

        queue = deque([root_context])
        visited = {}

        print("Root Context:")
        print(root_context.print_context())
        visited[root_context.id] = True

        print("\nChild Contexts:")

        while queue:
            current_context = queue.popleft()
            for child_context in current_context.children:
                if child_context not in visited.keys():
                    print(child_context.print_context())
                    queue.append(child_context)
                    visited[child_context] = True

    def visualize_network(self):
        g = pgv.AGraph(directed=True)

        root_context = self.root_context
        queue = deque([root_context])
        visited = {}

        while queue:
            current_context = queue.popleft()
            for child_context in current_context.children:
                g.add_edge(current_context.print_context(), child_context.print_context())
                if child_context not in visited.keys():
                    queue.append(child_context)
                    visited[child_context] = True

        g.layout(prog='dot')
        g.draw(f'collaboration_network_{root_context.id}_{datetime.datetime.now()}.png')
        print("Collaboration network visualization saved as collaboration_network.png")

    def share_resource(self, from_user_id: str, resource_id_to_share: str, to_user_ids: set[str]):

        # Get all users who are involved in the transaction
        involved_users = to_user_ids.union({from_user_id})

        # Start with the root context and do a Breadth-First-Search (BFS)
        root_context = self.root_context
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

                for child_context in current_context.children:

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

        self.contexts[correct_context].add_resource(resource_id_to_share)
        print(f"Correct Context: {correct_context}")

        # self.visualize_network()

    def unshare_resource(self, from_user_id: str, resource_id_to_unshare: str, to_user_ids: set[str]):
        # TODO: Wrong Behavior

        # Get all users who are involved in the transaction
        involved_users = to_user_ids.union({from_user_id})

        # Start with the root context and do a Breadth-First-Search (BFS)
        root_context = self.root_context
        queue = deque([root_context])
        visited = {}

        # The purpose is to find which context the resources are shared
        # The BFS Loop
        while queue:
            current_context = queue.popleft()

            users = current_context.get_users()
            resources = current_context.get_resources()

            # Only investigate a context if it includes all involved users
            if involved_users.issubset(users):

                # If the context has the shared resources
                # Remove the resource from the current context to the child without
                if resource_id_to_unshare in resources:

                    current_context.remove_resource(resource_id_to_unshare)

                    additional_users = users.difference(involved_users)
                    print(f"Additional Users: {additional_users}")
                    # If the context to unshare is a leaf node, then nothing else to do
                    if len(additional_users) == 0:
                        # self.visualize_network()
                        return

                    correct_users = additional_users.union({from_user_id})
                    correct_context_id = ''.join(sorted(correct_users))

                    for child_context in current_context.children:
                        if child_context.id == correct_context_id:
                            child_context.add_resource(resource_id_to_unshare)
                            # self.visualize_network()
                            return

            for child_context in current_context.children:
                if child_context not in visited.keys():
                    queue.append(child_context)
                    visited[child_context] = True

    def remove_user(self, user_id: str):
        pass

    def can_access(self, requester_id: str, resource_id: str) -> bool:

        resource = get_resource(resource_id)
        owner_id = resource.get_owner().get_uid()

        if requester_id == owner_id:
            return True

        involved_users = {owner_id, requester_id}

        root_context = self.root_context
        queue = deque([root_context])
        visited = {}

        while queue:

            current_context = queue.popleft()
            users = current_context.get_users()

            if involved_users.issubset(users):

                resources = current_context.get_resources()
                if resource_id in resources:
                    return True

            for child_context in current_context.children:
                if child_context not in visited.keys():
                    queue.append(child_context)
                    visited[child_context] = True

        return False
