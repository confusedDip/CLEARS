from ldap3 import Server, Connection


def connect_to_ldap(
        server_url="",  # Add your LDAP server URL here
        username="cn=admin,dc=rc,dc=example,dc=org",    # Add your LDAP admin username here
        password=""     # Add your LDAP admin password here
):
    server = Server(server_url)
    conn = Connection(server, user=username, password=password)
    conn.bind()
    return conn
