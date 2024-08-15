# Step-by-step Guide: Setting up a new Client Virtual Machine


### Virtual Machine Setup

For this tutorial, we assume a server VM `linux0` is already set up with necessary configurations and we aim to set up a client VM `linux1`. These VMs are connected through a `Bridged Adapter` and can interact with each other through `ping` and `ssh`. Both servers are running Ubuntu 22.04.3 LTS.

### Step 1: Share the File System from the linux0 Server

#### 1.1 Edit the `/etc/exports` File on linux0
On the file system server (e.g., `linux0`), update the `/etc/exports` file to share the directories with the new VM. You may add entries similar to:

```bash
/shared_directory  linux1_ip(rw,nohide,insecure,sync,no_subtree_check,no_roo_squash)
```

#### 1.2 Restart the NFS Server
After editing the /etc/exports file, restart the NFS server to apply the changes:

```bash
sudo service nfs-kernel-server restart
```

### Step 2: Mount the Directories on the Client VM

#### 2.1 Mount the Shared Directories
On the new VM, mount the directories shared from the host machine (`linux0`) using NFSv4:

```bash
sudo mount -o vers=4.0 linux0:/users /home
sudo mount -o vers=4.0 linux0:/scratch /scratch
sudo mount -o vers=4.0 linux0:/project /etc/project
sudo mount -o vers=4.0 linux0:/authz /usr/bin/authz
```

#### 2.2 Verify the Mounts
Check that the directories are correctly mounted:

```bash
nfsstat -m
```

### Step 3: Set up SLURM and MUNGE
Please follow the `slurm-setup.md` to set up Slurm Deamon (slurmd)


### Step 4: Set Up the LDAP Client

#### 4.1 Install LDAP Client Packages
Install the necessary LDAP client packages:

```bash
sudo apt-get install libnss-ldap libpam-ldap ldap-utils nscd
```

During installation, you will be prompted to configure the following:

```
LDAP URI: ldap://<ip of the ldap server>
Search Base: dc=rc,dc=example,dc=org
LDAP Version: 3
Make Local Root DB Admin: Yes
Does LDAP DB require login: No
LDAP Root Account: cn=admin,dc=rc,dc=example,dc=org
```

#### 4.2 Make Users and Groups Readable from LDAP
Edit the `/etc/nsswitch.conf` file to make users and groups readable from LDAP:

```plaintext
passwd:     compat ldap
group:      compat ldap
shadow:     compat ldap
```

#### 4.3 Configure PAM to Use LDAP for Authentication
PAM should automatically be configured during the installation. If not, manually edit the relevant files under `/etc/pam.d/`. For example, to configure PAM for authentication, add the following line to `/etc/pam.d/common-auth`, `/etc/pam.d/common-account`, etc.:

```plaintext
auth        [success=1 user_unknown=ignore default=die]     pam_ldap.so use_authtok try_first_pass
```

#### 4.4 Restart the Name Service Cache Daemon
Restart the nscd service to apply the changes:

```bash
sudo systemctl restart nscd
```
