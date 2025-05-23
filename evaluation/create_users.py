from ldap3 import Server, Connection, MODIFY_ADD

def connect_to_ldap(
        server_url="LDAP SERVER URL",
        username="cn=admin,dc=rc,dc=example,dc=org",
        password="LDAP SERVER PASSWORD"
):
    server = Server(server_url)
    conn = Connection(server, user=username, password=password)
    conn.bind()
    return conn

def create_group(conn, group_dn, group_name, gid_number):
    return conn.add(group_dn, ['top', 'posixGroup'], {'cn': group_name, 'gidNumber': gid_number})


def create_users(conn, n=1, uid_start=1001):
    base_dn = "ou=users,dc=rc,dc=example,dc=org"

    for i in range(1, n + 1):
        username = f"user_{i}"
        uid_number = uid_start + i - 1
        gid_number = uid_number
        user_dn = f"uid={username},{base_dn}"

        attributes = {
            'objectClass': ['inetOrgPerson', 'posixAccount', 'shadowAccount'],
            'uid': username,
            'sn': username.capitalize(),
            'givenName': username.capitalize(),
            'cn': username.capitalize(),
            'displayName': username.capitalize(),
            'uidNumber': str(uid_number),
            'gidNumber': str(gid_number),
            'userPassword': '',  # Placeholder
            'gecos': username.capitalize(),
            'loginShell': '/bin/bash',
            'homeDirectory': f"/home/{username}"
        }

        success = conn.add(user_dn, attributes=attributes)
        # Create default groups for the users
        success_group = create_group(
            conn=conn,
            group_dn=f"cn={username},ou=groups,dc=rc,dc=example,dc=org",
            group_name=username,
            gid_number=gid_number
        )

        if success and success_group:
            print(f"Added user: {username}")
        else:
            print(f"Failed to add user: {username} | {conn.result}")


def main():
    conn = connect_to_ldap()
    create_users(conn, n=100) # Create 100 users

if __name__ == "__main__":
    main()