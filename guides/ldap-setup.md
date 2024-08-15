# Step-by-step Guide: Setting up LDAP Server in the Controller VM

This guide provides step-by-step instructions for setting up an LDAP server on the controller node. You'll configure the LDAP server, create organizational units (OUs), and add users and groups using `.ldif` scripts.


### Virtual Machine Setup

For this tutorial, two VM servers with hostnames `linux0` and `linux2` have been set up. These VMs are connected through a `Bridged Adapter` and can interact with each other through `ping` and `ssh`. Both servers are running Ubuntu 22.04.3 LTS. This process can be extended to more than two servers.

## Step 1: Configure the LDAP Server

### 1.1 Run the LDAP Configuration Tool
Start by running the LDAP configuration tool to set up the LDAP server:
```bash
sudo dpkg-reconfigure slapd
```

Follow the prompts to configure the LDAP server, setting parameters like the domain name, organization name, and the administrative password.

For our setup, we have given, 
```bash
cn=admin,dc=rc,dc=example,dc=org
```

### 1.2 Verify the Configuration
The LDAP server configuration is stored in the `/etc/ldap.conf` file. Review this file to ensure that all settings are correct.

## Step 2: Create Organizational Units and Users/Groups with .ldif Scripts

### 2.1 Prepare the .ldif Files
You will need three .ldif files: `base.ldif, users.ldif`, and `groups.ldif`.

#### base.ldif
The base.ldif file creates the organizational units (OUs) for users and groups. The content of base.ldif should look like this:

```ldif
dn: ou=groups,dc=rc,dc=example,dc=org
objectClass: organizationalUnit
ou: groups

dn: ou=users,dc=rc,dc=example,dc=org
objectClass: organizationalUnit
ou: users
```

#### users.ldif
The users.ldif file adds individual user entries. For each user, create an entry like the following example for Alice:

```ldif
# Entry for Alice
dn: uid=alice,ou=users,dc=rc,dc=example,dc=org
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
uid: alice
sn: Alice
givenName: Alice
cn: Alice
displayName: Alice
uidNumber: 10001
gidNumber: 10001
userPassword: {SHA}<encrypted_password>
gecos: Alice
loginShell: /bin/bash
homeDirectory: /home/alice
```

#### groups.ldif
The groups.ldif file adds group entries corresponding to each user. Here’s an example for Alice's primary group:

```ldif
# Add entry for Alice's group
dn: cn=alice,ou=groups,dc=rc,dc=example,dc=org
changetype: add
objectClass: posixGroup
cn: alice
gidNumber: 10001
```

### 2.2 Run the .ldif Scripts
Use the ldapadd command to add the organizational units, users, and groups to the LDAP server.

#### Add Organizational Units
Run the following command to add the OUs defined in base.ldif:

```bash
ldapadd -x -W -D "cn=admin,dc=rc,dc=example,dc=org" -f base.ldif
```

#### Add Users
Next, add users using the users.ldif file:

```bash
ldapadd -x -W -D "cn=admin,dc=rc,dc=example,dc=org" -f users.ldif
```

#### Add Groups
Finally, add the groups using the groups.ldif file:

```bash
ldapadd -x -W -D "cn=admin,dc=rc,dc=example,dc=org" -f groups.ldif
```

Your LDAP server is now set up on the controller node, complete with organizational units, users, and groups. This configuration will allow the LDAP server to manage user authentication and group permissions across your network. This tutorial provides a clear guide for setting up an LDAP server on a controller node, including the configuration process and the addition of users and groups.






