import subprocess

def create_project(n=1):
    for i in range(1, n + 1):
        project_id = f"Project{i}"
        try:
            result = subprocess.run(
                ["clears", "start", "--mode=non-interactive", "-p", project_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            print(f"[✓] Created {project_id}: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"[✗] Failed to create {project_id}: {e.stderr.strip()}")

if __name__ == "__main__":
    create_project(n=100)