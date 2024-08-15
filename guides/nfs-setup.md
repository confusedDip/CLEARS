# Step-by-step Guide: Setting up Network File System (NFS) across Multiple Machines

To install NFS, administrative (sudo) access to the machines is required. This step-by-step tutorial explains how to set up and configure NFS on multiple Linux servers. 


### Virtual Machine Setup

For this tutorial, two VM servers with hostnames `linux0` and `linux2` have been set up. These VMs are connected through a `Bridged Adapter` and can interact with each other through `ping` and `ssh`. Both servers are running Ubuntu 22.04.3 LTS. This process can be extended to more than two servers.

<!-- > **NOTE:** For the example `bash` commands, any command that starts with just `$` is needed to be executed across all machines. Commands prefixed with `linux0$` is to be performed on the slurm controller node, and `linux2$` ones on every other node  -->

## 1. Create a Shared Network File System on the Server Machine

### Step 1.1: Update the System and Install NFS Server
On the root machine where the file system will be hosted, update the package list and install the NFS kernel server:
```bash!
sudo apt update
sudo apt install nfs-kernel-server
```

### Step 1.2: Create and Bind the Shared Directory
Create the directory that you want to share with other machines:
```bash!
sudo mkdir /export
sudo mkdir /export/shared_directory
```

Bind the original directory to the export directory:
```bash!
sudo mount --bind /original-directory /export/shared_directory
```

### Step 1.3: Update /etc/fstab
Edit the `/etc/fstab` file to make the bind mount persistent across reboots:

```bash!
sudo vim /etc/fstab
```

Add the following line:

```bash!
/original-directory /export/shared_directory ext4 bind,acl 0 0
```

### Step 1.4: Configure NFS Exports
Edit the `/etc/exports` file to specify which directory you want to share and the permissions:

```bash!
sudo vim /etc/exports
```

Add the following line to the file:
```bash!
/shared_directory  *(rw,nohide,insecure,sync,no_subtree_check,no_roo_squash)
```

### Step 1.5: Restart NFS Server
Restart the NFS kernel server to apply the changes:

```bash!
sudo service nfs-kernel-server restart
```

### Step 1.6: Export the Shared Directory
Apply the export configuration:

```bash!
sudo exportfs -a
```

Verify the status of the exports:

```bash!
sudo exportfs -v
```

## 2. Setup NFS on the Client Machines

### Step 2.1: Mount the NFS Share
On the client machine, ensure that you mount the NFS share with version 4.0:

```bash!
sudo mount -o vers=4.0 linux0:/shared_directory /mount_target
```

### Step 2.2: Verify the Mount
Check the NFS mount status:

```bash!
nfsstat -m
```
---

You have now set up an NFS shared directory across multiple Linux machines, using NFSv4 for the configuration. This guide should help you set up an NFS system on multiple Linux machines, allowing for shared access to directories.

