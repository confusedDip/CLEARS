import random
import subprocess
import time
import pandas as pd
random.seed(4)  # Reproducibility

# Configuration
initial_users = 3
max_users = 100
project_id = "Project1"
share_events = []
unshare_events = []

# Simulated state
active_users = set(f"user_{i}" for i in range(1, initial_users + 1))
all_users = [f"user_{i}" for i in range(1, max_users + 1)]

# Simulated share/unshare operation
def simulate_operation(op_type, from_user, to_users, resource):

    # Simulated latency (e.g., database, graph traversal, etc.)
    # time.sleep(random.uniform(0.005, 0.015))  # 5ms to 15ms
    # Observed latency

    start_time = time.perf_counter()
    subprocess.run([
        "clears", op_type, "--mode=non-interactive",
        "-p", project_id, "-o", from_user, "-u", *to_users
    ], check=True)
    end_time = time.perf_counter()

    latency = end_time - start_time
    return {
        "operation": op_type,
        "from_user": from_user,
        "to_users_count": len(to_users),
        "resource": resource,
        "latency": latency
    }

# Simulate system evolution
for tick in range(1, 201):  # 200 ticks (time steps)

    # Randomly add users to the project
    if len(active_users) < max_users and random.random() < 0.5:
        new_user = random.choice([u for u in all_users if u not in active_users])
        active_users.add(new_user)
        # Add collaborators
        subprocess.run([
            "sudo", "clears", "add", "--mode=non-interactive",
            "-p", project_id, "-u", new_user
        ], check=True)

    # Randomly remove users from the project
    if len(active_users) > initial_users and random.random() < 0.1:
        user_to_remove = random.choice(list(active_users))
        active_users.remove(user_to_remove)
        # Remove collaborators
        subprocess.run([
            "sudo", "clears", "remove", "--mode=non-interactive",
            "-p", project_id, "-u", user_to_remove
        ], check=True)

    # Perform random share/unshare operations
    user_list = list(active_users)
    for user in user_list:
        resource = f"/scratch/{user}"

        # Share
        if random.random() < 0.3:  # 30% chance to share
            collaborators = random.sample(user_list, random.randint(1, len(user_list)))
            collaborators = [u for u in collaborators if u != user]
            result = simulate_operation("share", user, collaborators, resource)
            share_events.append(result)

        # Unshare
        if random.random() < 0.2:  # 20% chance to unshare
            collaborators = random.sample(user_list, random.randint(1, len(user_list)))
            collaborators = [u for u in collaborators if u != user]
            result = simulate_operation("unshare", user, collaborators, resource)
            unshare_events.append(result)

if __name__ == "__main__":
    # Convert to DataFrame
    df_share = pd.DataFrame(share_events)
    df_unshare = pd.DataFrame(unshare_events)
