## Step-by-step Guide: Setting up Slurm across Multiple Machines

To install Slurm, administrative (sudo) access to the machines is required. This step-by-step tutorial explains how to set up and configure Slurm on multiple Linux servers. 
<!-- > **NOTE:** This is a minimal setup. It ignores setting up Slurm databases or Cgroups -->



### Virtual Machine Setup

For this tutorial, two VM servers with hostnames `linux0` and `linux2` have been set up. These VMs are connected through a `Bridged Adapter` and can interact with each other through `ping` and `ssh`. Both servers are running Ubuntu 22.04.3 LTS. This process can be extended to more than two servers.

> **NOTE:** For the example `bash` commands, any command that starts with just `$` is needed to be executed across all machines. Commands prefixed with `linux0$` is to be performed on the slurm controller node, and `linux2$` ones on every other node 


### Prerequisites
As per the [Super Quick Start](https://slurm.schedmd.com/quickstart_admin.html#quick_start) section in the official Slurm documentation, the following prerequisites must be met before setting up SLURM:

* Make sure the clocks, users and groups (UIDs and GIDs) are synchronized across the cluster.

* **Creating the Slurm User**:

    The `SlurmUser` must exist before starting Slurm and must have the same `uid` and `gid` on all nodes of the cluster. Create a `SlurmUser` named `slurm` on all machines.

    ```
    $ sudo  useradd -M slurm
    ```
    To verify whether the `uid` and `gid` for the `SlurmUser` are synchronized across machines, run the following command:
    ```
    $ id slurm
    (output) uid=1001(slurm) gid=1001(slurm) groups=1001(slurm)
    ```

* **Setting up Munge**:
    
    Install [MUNGE](https://dun.github.io/munge/) for authentication. Follow the steps to install, setup and configure MUNGE across machines.
    
    ```console
    # Create the munge user same as slurm user
    $ sudo useradd -M munge
    $ id munge
    (output) uid=1002(munge) gid=1002(munge) groups=1002(munge)
    
    # Install the necessary packages
    $ sudo apt install munge libmunge2 libmunge-dev
     
    # Verify if munge is installed successfully
    $ munge -n | unmunge | grep STATUS
    (output) STATUS:          Success (0)
    ```
    
    
    The next step is to generate MUNGE key, and have the same key across all machines. Repeat `linux2$` commands if there are more host nodes.
    
    ```console
    # Check if munge key is already generated in linux0
    linux0$ sudo cat /etc/munge/munge.key
    (output) <the munge key>
    
    # Transfer the munge key to linux2 through scp
    # Syntax: sudo scp source_path user@hostname:destination_path 
    linux0:$ sudo scp /etc/munge/munge.key user@linux2:key
    (output) munge.key                            100% 129 200.6KB/s 00:00
    
    # Check if the file is successfully copies in linux2
    linux2:$ ls
    (output) key
    
    # Copy this key to the linux2's munge key path
    linux2:$ sudo cp -f key /etc/munge/munge.key
    ```
    
    Now, setup the necessary file permissions for the `munge` user
    
    ```console
    $ sudo chown -R munge: /etc/munge/ /var/log/munge/ /var/lib/munge/ /run/munge/
    $ sudo chmod 0700 /etc/munge/ /var/log/munge/ /var/lib/munge/
    $ sudo chmod 0755 /run/munge/
    ```
    
    Then, enable and start the munge service in all machines
    > **NOTE:** Remember to not use sudo when running munge

    ```console
    $ systemctl enable munge    
    $ systemctl start munge
    $ systemctl status munge
    (output)
       Loaded: loaded (/lib/systemd/system/munge.service; enabled; vendor preset: enabled)
       Active: active (running) since Thu 2024-02-08 22:33:18 UTC; 1h 1min ago
         Docs: man:munged(8)
      Process: 8481 ExecStart=/usr/sbin/munged $OPTIONS (code=exited, status=0/SUCCESS)
     Main PID: 8483 (munged)
        Tasks: 4 (limit: 4558)
       Memory: 924.0K
          CPU: 90ms
       CGroup: /system.slice/munge.service
             └─8483 /usr/sbin/munged

    Feb 08 22:33:18 linux0 systemd[1]: Starting MUNGE authentication service...
    Feb 08 22:33:18 linux0 systemd[1]: Started MUNGE authentication service.
    ```
    


### Install and Setup Slurm

*
    Install the `slurm-wlm` package and check the version of SLURM in all machines. It is important to have the same version SLURM across all machines
    
    ```console
    $ sudo apt install slurm-wlm
    $ slurmd -V
    (output) slurm-wlm 21.08.5
    ```

*
    Now, as per the version, go to the [Slurm Configuration Tool](https://slurm.schedmd.com/archive/slurm-21.08.5/configurator.html) and fill out the details.
    
    > **Note:** It is important to note that the slurm version might not be the latest, and hence the default [Slurm Configuration Tool](https://slurm.schedmd.com/configurator.html) might not work. It is important to go to archive websites and use the tool which matches the Slurm version in your machine
    

*
    Copy the output of the configuration file and paste it in the Slurm Configuration File path across all machines
    
    ```console
    $ sudo vim /etc/slurm/slurm.conf
    (Paste the contents and save the file)
    ```

*
    Now, it is important to update the necessary file permission of the `SlurmUser`. The file paths can be obtained from the `slurm.conf` file. If the files/directories do not exist, create one. 
    
    ```console
    # Create the files and directories that do not exist
    $ sudo touch /var/log/slurmd.log
    $ sudo touch /var/log/slurmctld.log
    $ sudo mkdir -p /var/spool/slurmd /var/spool/slurmctld
    $ sudo touch /var/run/slurmctld.pid
    $ sudo touch /var/run/slurmd.pid
    
    # Update the permissions
    $ sudo chown -R slurm: /var/log/slurmctld.log /var/log/slurmd.log 
    $ sudo chmod 0777 /var/log/slurmctld.log /var/log/slurmd.log 
    $ sudo chown -R slurm: /var/spool/slurmd /var/spool/slurmctld/
    $ sudo chmod 0755 /var/spool/slurmd /var/spool/slurmctld/
    $ sudo chown -R slurm: /var/run/slurmctld.pid /var/run/slurmd.pid
    $ sudo chmod 0755 /var/run/slurmctld.pid /var/run/slurmd.pid

    ```
    
*
    Finally, enable and start the Slurm Controller Daemon`slurmctld` in `linux0` and the Slurm Daemon in `linux2`
    
    ```console

    linux0:$ systemctl enable slurmctld
    linux0:$ systemctl start slurmctld
    linux0:$ systemctl status slurmctld
    (output)
    ● slurmctld.service - Slurm controller daemon
         Loaded: loaded (/lib/systemd/system/slurmctld.service; enabled; vendor preset: enabled)
         Active: active (running) since Thu 2024-02-08 22:34:05 UTC; 1h 22min ago
           Docs: man:slurmctld(8)
       Main PID: 8504 (slurmctld)
          Tasks: 10
         Memory: 5.5M
            CPU: 3.928s
         CGroup: /system.slice/slurmctld.service
             ├─8504 /usr/sbin/slurmctld -D -s
             └─8506 "slurmctld: slurmscriptd" "" ""
    ```
    ```console
    linux2:$ systemctl enable slurmd
    linux2:$ systemctl start slurmd
    linux2:$ systemctl status slurmd
    (output)

    ● slurmd.service - Slurm node daemon
         Loaded: loaded (/lib/systemd/system/slurmd.service; enabled; vendor preset: >
         Active: active (running) since Thu 2024-02-08 22:34:16 UTC; 1h 23min ago
           Docs: man:slurmd(8)
       Main PID: 4024 (slurmd)
          Tasks: 1
         Memory: 1.4M
            CPU: 221ms
         CGroup: /system.slice/slurmd.service
             └─4024 /usr/sbin/slurmd -D -s

    ```
    > In case you see any error, investigate it through the following commands
    ```console
    # slurmctld errors
    linux0:$ sudo journalctl -xe | grep slurmctld
    linux0:$ sudo cat /var/log/slurmctld.log
    
    # slurmd errors
    linux2:$ sudo journalctl -xe | grep slurmd
    linux2:$ sudo cat /var/log/slurmd.log
    ```
*
    You can verify whether both `slurmctld` and `slurmd` are running and communicating properly, run the following commands.
    
    ```console
    $ sinfo
    (output)
    PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST
    debug*       up   infinite      1   idle linux2
    ```
    
*
    Voila! You have successfully set up MUNGE and Slurm across multiple Linux machines.
    

