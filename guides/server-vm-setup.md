# Step-by-step Guide: Setting up the Controller (Server) Virtual Machine


### Virtual Machine Setup

For this tutorial, we set up the server VM `linux0`. This VM is connected with one or more client VMs through a `Bridged Adapter` and can interact with them through `ping` and `ssh`. All VMs are running Ubuntu 22.04.3 LTS.

## Step 1: Share the File System

In our experimental setup, we have hosted the shared network file system at the controller server itself. Please follow the step by step guide in `nfs-setup.md` to configure the shared file system.
a
## Step 2: Configure LDAP

In our experimental setup, we have hosted the LDAP server at the controller server itself. Please follow the step by step guide in `ldap-setup.md` to configure the shared file system.

## Step 3: Configure SLURM and MUNGE

In our experimental setup, we have designated the controller server as the slurm controller. Please follow the step by step guide in `slurm-setup.md` to configure Slurm controller daemon (slurmctld).
