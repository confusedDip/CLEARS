from ldap3 import MODIFY_DELETE


def remove_user_from_group(conn, group_dn, user_uid):

    success = conn.modify(group_dn, {'memberUid': [(MODIFY_DELETE, [user_uid])]})

    if success:
        print(f"Successfully removed {user_uid} from {group_dn}")
    else:
        print(f"Failed to remove {user_uid} from {group_dn}")
        print(f"Result: {conn.result}")
        print(f"Response: {conn.response}")
