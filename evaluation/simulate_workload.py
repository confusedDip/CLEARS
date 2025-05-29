import random
import subprocess
import time
import pandas as pd
from collections import defaultdict
import json

# random.seed(5)

# Counts the active context
def count_active_contexts(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    active_count = sum(
        1 for context in data.get("contexts", {}).values()
        if context.get("resource_ids") and len(context["resource_ids"]) > 0
    )

    return active_count

# Simulated share/unshare operation
def simulate_operation(project_id, op_type, from_user, to_users, resource):
    start_time = time.perf_counter()
    subprocess.run([
        "clears", op_type, "--mode=non-interactive",
        "-p", project_id, "-o", from_user, "-u", *to_users,
        "-r", resource, "-t", "1"
    ], check=True)
    end_time = time.perf_counter()

    latency = end_time - start_time
    network_file_path = f"/etc/project/{project_id}.json"
    return {
        "operation": op_type,
        "from_user": from_user,
        "to_users_count": len(to_users),
        "resource": resource,
        "latency": latency,
        "num_contexts": count_active_contexts(network_file_path)
    }

def main(index):
    random.seed(index)
    initial_users = 20
    max_users = 100
    project_id = f"Project{index}"

    # share_events = []
    # unshare_events = []
    # summary_by_timestamp = []

    active_users = set(f"user_{i}" for i in range(1, initial_users + 1))
    all_users = [f"user_{i}" for i in range(1, max_users + 1)]

    shared_state = defaultdict(set)

    # Add initial set of users
    for user in active_users:
        subprocess.run([
            "sudo", "clears", "add", "--mode=non-interactive",
            "-p", project_id, "-u", user
        ], check=True)

    n_timestamps = 100

    # Initialize CSV files
    share_path = f"df_share_{index}.csv"
    unshare_path = f"df_unshare_{index}.csv"
    summary_path = f"df_summary_{index}.csv"
    df_share_header_written = False
    df_unshare_header_written = False
    df_summary_header_written = False

    for tick in range(0, n_timestamps):
        share_count = 0
        unshare_count = 0
        total_latency = 0.0
        share_events = []
        unshare_events = []

        # Experiment 1 Workload
        # if tick < n_timestamps / 2:
        #     share_probability = 0.9
        #     unshare_probability = 0.1
        #     add_probability = 0.5
        #     remove_probability = 0.1
        # else:
        #     share_probability = 0.2
        #     unshare_probability = 0.8
        #     add_probability = 0.1
        #     remove_probability = 0.8

        # Experiment 2 Workload
        share_probability = 1 - int(tick / 10) * 0.1
        unshare_probability = 1 - share_probability
        add_probability = 0.8 * (1 - int(tick / 50))
        remove_probability = 0.8 * int(tick / 50)

        # if tick < n_timestamps / 2: # 0 - 49
        #     add_probability = 0.8
        #     remove_probability = 0.0
        # else: # 50 - 99
        #     add_probability = 0.0
        #     remove_probability = 0.8

        if len(active_users) < max_users and random.random() < add_probability:
            for _ in range(2):  # Add two users
                new_user = random.choice([u for u in all_users if u not in active_users])
                active_users.add(new_user)
                print(f"tick: {tick}", flush=True)
                subprocess.run([
                    "sudo", "clears", "add", "--mode=non-interactive",
                    "-p", project_id, "-u", new_user
                ], check=True)

        if len(active_users) > initial_users and random.random() < remove_probability:
            for _ in range(2):  # Remove two users
                user_to_remove = random.choice(list(active_users))
                active_users.remove(user_to_remove)
                print(f"tick: {tick}", flush=True)
                subprocess.run([
                    "sudo", "clears", "remove", "--mode=non-interactive",
                    "-p", project_id, "-u", user_to_remove
                ], check=True)
                if user_to_remove in shared_state:
                    del shared_state[user_to_remove]
                for k in shared_state:
                    shared_state[k].discard(user_to_remove)

        user_list = list(active_users)
        for user in user_list:
            resource = f"/scratch/{user}"

            if random.random() < share_probability:
                potential_targets = [u for u in user_list if u != user]
                to_share = random.sample(potential_targets, random.randint(1, len(potential_targets)))
                print(f"tick: {tick}")
                result = simulate_operation(project_id, "share", user, to_share, resource)
                share_events.append(result)
                total_latency += result["latency"]
                share_count += 1
                shared_state[user].update(to_share)

            if shared_state[user] and random.random() < unshare_probability:
                max_subset_size = len(shared_state[user])
                to_unshare = random.sample(list(shared_state[user]), random.randint(1, max_subset_size))
                print(f"tick: {tick}")
                result = simulate_operation(project_id, "unshare", user, to_unshare, resource)
                unshare_events.append(result)
                total_latency += result["latency"]
                unshare_count += 1
                shared_state[user].difference_update(to_unshare)

        # Write incremental data to CSVs
        if share_count > 0:
            pd.DataFrame(share_events).to_csv(
                share_path, mode='a', header=not df_share_header_written, index=False
            )
            df_share_header_written = True

        if unshare_count > 0:
            pd.DataFrame(unshare_events).to_csv(
                unshare_path, mode='a', header=not df_unshare_header_written, index=False
            )
            df_unshare_header_written = True


        pd.DataFrame([{
            "timestamp": tick,
            "share_count": share_count,
            "unshare_count": unshare_count,
            "total_latency": total_latency
        }]).to_csv(
            summary_path, mode='a', header=not df_summary_header_written, index=False
        )
        df_summary_header_written = True

        # summary_by_timestamp.append({
        #     "timestamp": tick,
        #     "share_count": share_count,
        #     "unshare_count": unshare_count,
        #     "total_latency": total_latency
        # })

    # return share_events, unshare_events, summary_by_timestamp


# Run and export
if __name__ == "__main__":

    for i in range(11, 12):
        # share_events_res, unshare_events_res, summary_stats = main(i)
        # df_share = pd.DataFrame(share_events_res)
        # df_unshare = pd.DataFrame(unshare_events_res)
        # df_summary = pd.DataFrame(summary_stats)
        #
        # # df_share.to_csv(f"results/run{i}/df_share.csv")
        # # df_unshare.to_csv(f"results/run{i}/df_unshare.csv")
        # # df_summary.to_csv(f"results/run{i}/df_summary.csv")
        #
        # df_share.to_csv(f"df_share_{i}.csv")
        # df_unshare.to_csv(f"df_unshare_{i}.csv")
        # df_summary.to_csv(f"df_summary_{i}.csv")
        main(i)