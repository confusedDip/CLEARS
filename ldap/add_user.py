from ldap3 import MODIFY_ADD


def add_user_to_group(conn, group_dn, user_uid):
    conn.modify(group_dn, {'memberUid': [(MODIFY_ADD, [user_uid])]})
