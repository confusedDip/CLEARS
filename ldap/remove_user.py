from ldap3 import MODIFY_DELETE


def remove_user_from_group(conn, group_dn, user_uid):
    conn.modify(group_dn, {'memberUid': [(MODIFY_DELETE, [user_uid])]})
