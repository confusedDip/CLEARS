import subprocess
import random
from collections import defaultdict

random.seed(4)  # Reproducibility

def assign_users(n_projects=100, n_users=1000):
    all_users = [f"user_{i}" for i in range(1, n_users + 1)]
    user_project_map = defaultdict(set)
    project_ids = [f"Project{i}" for i in range(1, n_projects + 1)]

    print(f"Distributing {n_users} users to {n_projects} projects...")

    # Phase 1: Initial random assignment
    for i in range(1, n_projects+1):
        num_users = i+2 # Users in projects ranges from 3 to n_projects+2
        project_id = f"Project{i}"
        assigned_users = random.sample(all_users, num_users)
        for u in assigned_users:
            user_project_map[u].add(project_id)

        # Add collaborators
        subprocess.run([
            "sudo", "clears", "add", "--mode=non-interactive",
            "-p", project_id, "-u", *assigned_users
        ], check=True)

    # Phase 2: Ensure all users are included
    unassigned_users = [user for user in all_users if not user_project_map[user]]
    if unassigned_users:
        print(f"Assigning {len(unassigned_users)} previously unassigned users...")

    for user in unassigned_users:
        project_id = random.choice(project_ids)
        subprocess.run([
            "sudo", "python3", main_script, "add", "--mode=non-interactive",
            "-p", project_id, "-u", user
        ], check=True)
        user_project_map[user].add(project_id)

    print(f"✅ All {n_projects} projects created and all {n_users} users assigned to at least one project.")
