from ldap3 import MODIFY_ADD


def create_group(conn, group_dn, group_name, gid_number):
    return conn.add(group_dn, ['top', 'posixGroup'], {'cn': group_name, 'gidNumber': gid_number})
