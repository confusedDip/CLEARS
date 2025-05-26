#!/usr/bin/python3

import os
from ldap3 import Server, Connection, ALL, SUBTREE

def connect_to_ldap(
        server_url="192.168.29.150",
        username="cn=admin,dc=rc,dc=example,dc=org",
        password="Bally@2016"
):
    server = Server(server_url)
    conn = Connection(server, user=username, password=password)
    conn.bind()
    return conn

USER_BASE_DN = 'ou=users,dc=rc,dc=example,dc=org'

def create_scratch_directory():
    if not os.path.exists('/scratch'):
        os.makedirs('/scratch')
        print("Created /scratch directory.")

def create_user_dirs_from_ldap():
    # Connect to LDAP
    conn = connect_to_ldap()

    # Search for all users
    conn.search(search_base=USER_BASE_DN,
                search_filter='(objectClass=posixAccount)',
                search_scope=SUBTREE,
                attributes=['uid', 'uidNumber', 'gidNumber'])

    create_scratch_directory()

    # For each user, create a directory in /scratch
    for entry in conn.entries:
        username = entry.uid.value
        uid_number = int(entry.uidNumber.value)
        gid_number = int(entry.gidNumber.value)
        user_dir = os.path.join('/scratch', username)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
            print(f"Created directory: {user_dir}")
        else:
            print(f"Directory already exists: {user_dir}")

        # Set ownership
        try:
            os.chown(user_dir, uid_number, gid_number)
            print(f"Set ownership of {user_dir} to UID:{uid_number}, GID:{gid_number}")
        except PermissionError as e:
            print(f"⚠️  Failed to set ownership for {user_dir}: {e}")

    conn.unbind()

if __name__ == "__main__":
    create_user_dirs_from_ldap()
