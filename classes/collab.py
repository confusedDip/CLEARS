import datetime
from collections import deque
from itertools import combinations
import pygraphviz as pgv


class Context:

    def __init__(self, users):
        self.id = ''.join(sorted(users))
        self.users = set(users.copy())
        self.resources = set()
        self.parents = set()
        self.children = set()

    def get_users(self):
        return self.users

    def get_resources(self):
        return self.resources

    def add_resource(self, resource):
        self.resources.add(resource)

    def remove_resource(self, resource):
        self.resources.remove(resource)

    def print_context(self):
        context_str = (f"{self.id}\n" + "{" + ', '.join(list(self.users)) + "}" +
                       "\n" "[" + ', '.join(list(self.resources)) + "]")
        # print(context_str)
        return context_str


class Network:

    def __init__(self, users):
        self.all_users = users
        self.contexts = {}
        self.create_network()

    def add_new_user(self, user):
        self.all_users.append(user)
        self.expand_network()

    def add_context(self, context):

        if context.id not in self.contexts.keys():
            self.contexts[context.id] = context

    def create_network(self):

        root_context = Context(self.all_users)
        self.add_context(root_context)

        # Recursively generate child contexts with one less user until leaf level with two users
        self.generate_child_contexts(root_context, len(self.all_users))

    def expand_network(self):

        new_root_context = Context(self.all_users)
        self.add_context(new_root_context)

        # Recursively generate child contexts with one less user until leaf level with two users
        self.generate_child_contexts(new_root_context, len(self.all_users))

    def generate_child_contexts(self, parent_context, num_users):

        if num_users <= 2:
            return

        # Generate child contexts with one less user
        user_combinations = [list(comb) for comb in combinations(parent_context.users, num_users - 1)]

        for child_users in user_combinations:

            child_context_id = ''.join(sorted(child_users))

            if child_context_id in self.contexts.keys():
                child_context = self.contexts[child_context_id]

            else:
                child_context = Context(child_users)
                self.add_context(child_context)

            parent_context.children.add(child_context)
            child_context.parents.add(parent_context)

            self.generate_child_contexts(child_context, num_users - 1)

    def print_network(self):

        root_context = self.contexts[''.join(self.all_users)]

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
        G = pgv.AGraph(directed=True)

        root_context = self.contexts[''.join(self.all_users)]
        queue = deque([root_context])
        visited = {}

        while queue:
            current_context = queue.popleft()
            for child_context in current_context.children:
                G.add_edge(current_context.print_context(), child_context.print_context())
                if child_context not in visited.keys():
                    queue.append(child_context)
                    visited[child_context] = True

        G.layout(prog='dot')
        G.draw(f'collaboration_network_{root_context.id}_{datetime.datetime.now()}.png')
        print("Collaboration network visualization saved as collaboration_network.png")

    def share_resource(self, from_user, resource_to_share, to_users):

        involved_users = to_users.union({from_user})

        root_context = self.contexts[''.join(self.all_users)]
        queue = deque([root_context])
        visited = {}

        already_shared_context = None

        while queue:
            current_context = queue.popleft()

            resources = current_context.get_resources()

            if resource_to_share in resources:

                already_shared_context = current_context
                current_context.remove_resource(resource_to_share)
                break

            else:
                for child_context in current_context.children:
                    if child_context not in visited.keys():
                        queue.append(child_context)
                        visited[child_context] = True

        if already_shared_context is None:
            correct_context = ''.join(sorted(involved_users))
        else:
            already_shared_users = already_shared_context.get_users()
            correct_users = involved_users.union(already_shared_users)
            correct_context = ''.join(sorted(correct_users))

        self.contexts[correct_context].add_resource(resource_to_share)
        print(f"Correct Context: {correct_context}")

        self.visualize_network()

    def unshare_resource(self, from_user, resource_to_unshare, to_users):

        involved_users = to_users.union({from_user})

        root_context = self.contexts[''.join(self.all_users)]
        queue = deque([root_context])
        visited = {}

        while queue:
            current_context = queue.popleft()

            users = current_context.get_users()
            resources = current_context.get_resources()

            if involved_users.issubset(users):
                if resource_to_unshare in resources:

                    current_context.remove_resource(resource_to_unshare)

                    additional_users = users.difference(involved_users)
                    print(f"Additional Users: {additional_users}")
                    # If the context to unshare is a leaf node, then nothing else to do
                    if len(additional_users) == 0:
                        self.visualize_network()
                        return

                    correct_users = additional_users.union({from_user})
                    correct_context_id = ''.join(sorted(correct_users))

                    for child_context in current_context.children:
                        if child_context.id == correct_context_id:
                            child_context.add_resource(resource_to_unshare)
                            self.visualize_network()
                            return

            for child_context in current_context.children:
                if child_context not in visited.keys():
                    queue.append(child_context)
                    visited[child_context] = True
