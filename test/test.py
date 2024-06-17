import os


def access_directory(path: str) -> bool:
    print("Attempting to access: ", path)
    try:
        os.chdir(path)
        print("Decision: Permit")
        return True
    except PermissionError:
        print("Decision: Deny")
        return False


def main():
    directories = [
        "/scratch/alice",
        "/scratch/alex",
        "/scratch/bob",
        "/scratch/bailey",
        "/scratch/connor",
        "/scratch/cathy",
        "/scratch/dave",
        "/scratch/drew",
        "/data/alice",
        "/data/alex",
        "/data/bob"
    ]

    for directory in directories:
        access_directory(directory)


if __name__ == "__main__":
    main()
