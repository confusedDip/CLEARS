from ldap3 import Server, Connection


def connect_to_ldap(
        server_url="ldap://10.218.108.176",
        username="cn=admin,dc=rc,dc=example,dc=org",
        password="Bally@2016"
):
    server = Server(server_url)
    conn = Connection(server, user=username, password=password)
    conn.bind()
    return conn
