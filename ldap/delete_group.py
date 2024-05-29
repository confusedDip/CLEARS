def delete_group(conn, group_dn):
    success = conn.delete(group_dn)

    if success:
        print(f"Successfully deleted group {group_dn}")
    else:
        print(f"Failed to remove group {group_dn}")
        print(f"Result: {conn.result}")
        print(f"Response: {conn.response}")
