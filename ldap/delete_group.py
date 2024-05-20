def delete_group(conn, group_dn):
    conn.delete(group_dn)
