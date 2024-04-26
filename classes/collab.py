from collections import deque
from itertools import combinations
import pygraphviz as pgv

class Context:

    def __init__(self, users):
        self.id = ''.join(sorted(users))
        self.users = users.copy()
        self.resources = []
        self.parents = []
        self.children = []
    
    def get_users(self):
        return self.users
    
    def add_resources(self, resources):
        self.resources = resources
    
    def print_context(self):

        context_str = f"{self.id}\n" + "{" + ', '.join(self.users) +"}" + "\n" "[ " + ', '.join(self.resources) +"]"
        # print(context_str)
        return context_str
        

class Network:

    def __init__(self, users):
        self.all_users = users
        self.contexts = {}
        self.create_network()
    
    def add_new_user(self, user):
        self.all_users.append(user)
        self.update_network()

    def add_context(self, context):

        if context.id not in self.contexts.keys():
            self.contexts[context.id] = context
        

    def create_network(self):

        root_context = Context(self.all_users)
        self.add_context(root_context)

        # Recursively generate child contexts with one less user until leaf level with two users
        self.generate_child_contexts(root_context, len(self.all_users))



    def update_network(self):

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

            parent_context.children.append(child_context)
            child_context.parents.append(parent_context)

            self.generate_child_contexts(child_context, num_users - 1)


    def print_network(self):
        
        root_context = self.contexts[''.join(self.all_users)]
        
        queue = deque([root_context])
        visited = {}

        print("Root Context:")
        root_context.print_context()
        visited[root_context.id] = True

        print("\nChild Contexts:")

        while queue:
            current_context = queue.popleft()
            for child_context in current_context.children:
                if child_context not in visited.keys():
                    child_context.print_context()
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
        G.draw(f'collaboration_network_{root_context.id}.png')
        print("Collaboration network visualization saved as collaboration_network.png")


    def update_context_resource(self, from_user, resource, to_users):

        involved_users = to_users.append(from_user)
        root_context = self.contexts[''.join(self.all_users)]
        queue = deque([root_context])
        visited = {}

        while queue:
            current_context = queue.popleft()
            
            current_context_users = current_context.get_users()

            if all(user in current_context_users for user in involved_users):
                
                other_users = list(set(current_context_users) - set(involved_users))

                
            
            for child_context in current_context.children:
                if child_context not in visited.keys():
                    queue.append(child_context)
                    visited[child_context] = True

