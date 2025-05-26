import random
import subprocess
import time
import pandas as pd
random.seed(4)  # Reproducibility



# Simulated share/unshare operation
def simulate_operation(project_id, op_type, from_user, to_users, resource):

    # Simulated latency (e.g., database, graph traversal, etc.)
    # time.sleep(random.uniform(0.005, 0.015))  # 5ms to 15ms
    # Observed latency

    start_time = time.perf_counter()
    subprocess.run([
        "clears", op_type, "--mode=non-interactive",
        "-p", project_id, "-o", from_user, "-u", *to_users,
        "-r", resource, "-t", "1"
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

def main():

    # Configuration
    initial_users = 3
    max_users = 100
    project_id = "Project4"
    share_events = []
    unshare_events = []

    # Simulated state
    active_users = set(f"user_{i}" for i in range(1, initial_users + 1))
    all_users = [f"user_{i}" for i in range(1, max_users + 1)]

    # Add active users to the project
    for user in active_users:
        subprocess.run([
            "sudo", "clears", "add", "--mode=non-interactive",
            "-p", project_id, "-u", user
        ], check=True
        )

    n_timestamps = 5

    # Simulate system evolution
    for tick in range(1, n_timestamps):  # 200 ticks (time steps)


        if tick < n_timestamps / 2: # First half of the scenario
            share_probability = 0.9
            unshare_probability = 0.1
            add_probability = 0.5
            remove_probability = 0.1
        else: # Second half of the scenario
            share_probability = 0.2
            unshare_probability = 0.8
            add_probability = 0.1
            remove_probability = 0.8

        # Randomly add users to the project
        if len(active_users) < max_users and random.random() < add_probability:
            new_user = random.choice([u for u in all_users if u not in active_users])
            active_users.add(new_user)
            # Add collaborators
            subprocess.run([
                "sudo", "clears", "add", "--mode=non-interactive",
                "-p", project_id, "-u", new_user
            ], check=True)

        # Randomly remove users from the project
        if len(active_users) > initial_users and random.random() < remove_probability:
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
            if random.random() < share_probability:  # 30% chance to share
                collaborators = random.sample(user_list, random.randint(1, len(user_list)))
                collaborators = [u for u in collaborators if u != user]
                result = simulate_operation(project_id,"share", user, collaborators, resource)
                share_events.append(result)

            # Unshare
            if random.random() < unshare_probability:  # 20% chance to unshare
                collaborators = random.sample(user_list, random.randint(1, len(user_list)))
                collaborators = [u for u in collaborators if u != user]
                result = simulate_operation(project_id,"unshare", user, collaborators, resource)
                unshare_events.append(result)

    return share_events, unshare_events

if __name__ == "__main__":
    # Convert to DataFrame
    share_events_res, unshare_events_res = main()
    df_share = pd.DataFrame(share_events_res)
    df_unshare = pd.DataFrame(unshare_events_res)
    print(df_share)
    print(df_unshare)
