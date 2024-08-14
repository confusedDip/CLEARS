from ldap3 import Server, Connection


def connect_to_ldap(
        server_url="LDAP SERVER URL",
        username="cn=admin,dc=rc,dc=example,dc=org",
        password="LDAP SERVER PASSWORD"
):
    server = Server(server_url)
    conn = Connection(server, user=username, password=password)
    conn.bind()
    return conn
