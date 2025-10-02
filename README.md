
# CLEARS: Collaboration-Aware Authorization for Resource Sharing  

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)  [![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)  [![Platform](https://img.shields.io/badge/Platform-Linux-orange)](#environmental-setup)  

---
  

**Paper:** Towards Collaboration-Aware Resource Sharing in Research Computing Infrastructures

  

**Authors:** Souradip Nath, Ananta Soneji, Jaejong Baek, Carlos Rubio-Medrano and Gail-Joon Ahn

  

**Abstract:** As scientific research grows increasingly collaborative, data-driven, and computation-intensive, Research Computing Infrastructures (RCIs) have emerged as critical platforms for enabling scientific collaboration across diverse disciplines. These infrastructures offer advanced computational and storage solutions essential for collaborative research, yet securing shared access to such resources remains a significant challenge. Consequently, there has been limited investigation into how collaboration context is conceptualized and leveraged during access provisioning, especially within RCIs. In this paper, we investigate existing resource sharing practices within RCIs, revealing key gaps in their ability to support secure authorization within dynamic, project-driven collaborative workflows. Building on these insights, we introduce a framework called CLEARS (Collaboration-Aware Authorization for Resource Sharing) that formally represents collaboration contexts and operationalizes them to guide secure, context-aware, and dynamically evolving resource sharing authorization throughout the collaboration lifecycle. Through experiments, we demonstrate that CLEARS delivers precise access enforcement under evolving collaborative scenarios while maintaining minimal execution overhead.

## 📂 Repository Structure  
  

```bash
.
├── guides/                 # Step-by-step environment setup
│   ├── client-vm-setup.md
│   ├── ldap-setup.md
│   ├── nfs-setup.md
│   ├── server-vm-setup.md
│   └── slurm-setup.md
├── install.sh              # Installation script
├── requirements.txt        # Dependencies
├── main.py                 # Main entry point (CLI tool: clears)
├── classes/                # Core class definitions
│   └── collab.py
├── utilities/              # Utility functions + C wrappers
│   ├── collab.py
│   ├── wrapper_network_dump(.c)
│   └── wrapper_supdate(.c)
├── ldap/                   # LDAP-related operations
│   ├── add_user.py
│   ├── connect_ldap.py
│   ├── create_group.py
│   ├── delete_group.py
│   └── remove_user.py
└── evaluation/             # Evaluation scripts and results
    ├── eval.py
    ├── simulate_workload.py
    └── results/runXX/df_*.csv  
```
## ⚙️ Environmental Setup

  

The implementation is tested in a **simulated RCI environment** with three virtual machines:

-   `linux0`, `linux1`, `linux3`
-   OS: **Ubuntu 22.04.03 LTS Server**
-   Network: **Bridged** via Intel PRO/1000 MT Desktop adapter
    

➡️ For high-level details, please read [`Appendix.pdf`](https://github.com/confusedDip/CLEARS/blob/main/Appendix.pdf)

➡️ For detailed VM setup instructions, see the [`guides`](https://github.com/confusedDip/CLEARS/tree/main/guides) folder.

  

## Installation

 ## 🚀 Installation

1️⃣ Clone the Repository

`git clone <repository-url> cd clears` 

2️⃣ Update the `server_url`, admin `username` and `password` in `ldap/connect_ldap.py`

3️⃣ Run the Installation Script

`./install.sh` 

This script:

-   Installs dependencies
-   Compiles C wrappers
-   Sets up system directories & symbolic links
-   Prepares `clears` as a global command
    

Once complete, you can run:

`clears help` 

## 💻 Usage

The **`clears`** CLI tool allows administrators to manage shared privileges in collaborative projects.

### 🔑 Available Commands
  

```bash

clears(1)

NAME
clears  -  efficiently  manage  shared  privileges

SYNOPSIS
clears [COMMAND..]
  
COMMANDS

start  Start  a  new  project. (requires administrative  privileges  to  perform)
add  Add  collaborators  to  an  existing  project. (requires administrative  privileges  to  perform)
share  Share  privileges  with  a  collaborator  to  access  resources  within  a  project.
unshare  Retract  previously  shared  privileges  from  a  collaborator  within  a  project.
remove  Remove  collaborators  from  an  existing  project. (requires administrative  privileges  to  perform)
end End an existing project. (requires  administrative  privileges  to  perform)
help  Launch  the  help  menu.

```

### 🖥️ Example CLI Workflow
  
There are two modes in which `clears` could be used: `interactive` (default) and `non-interactive` (for testing). 

The following snippets illustrate the command line interface for various commands of the interactive mode of the `clears` tool. In these examples, we have one system administrator, `sysadmin`, with elevated privileges, and three regular users: `alex`, `bailey`, and `cathy`.

  

```bash

# start

sysadmin@linux0:~$  sudo  clears  start
Enter  the  project  name:  Project1
Project  '/etc/project/Project1.json'  created/updated  successfully.  

# add

sysadmin@linux0:~$  sudo  clears  add
Enter  the  project  name:  Project1
Enter  the  user  names  to  add (space separated): alex bailey cathy
bailey(uid=10002) successfully added to Project1
cathy(uid=10003) successfully added to Project1
alex(uid=10001) successfully added to Project1
Project  '/etc/project/Project1.json'  created/updated  successfully.

# share

alex@linux1:~$  clears  share
Enter  the  project  name:  Project1
Enter  the  resource  type  you  want  to  share:
Submit  1  for  Files/Directories
Submit  2  for  Computational  Partition
> 1
Enter  the  resource  name  you  want  to  share:  /scratch/alex
Enter  the  user  names  to  share  with (space separated): bailey cathy
Sharing  /scratch/alex  Allowed:  From  alex  to  bailey
Sharing  /scratch/alex  Allowed:  From  alex  to  cathy
Collaboration  '{'alex', 'bailey', 'cathy'}'  granted  access  to  resource  '/scratch/alex'.
Project  '/etc/project/Project1.json'  created/updated  successfully.
  
# unshare

alex@linux1:~$  clears  unshare
Enter  the  project  name:  Project1
Enter  the  resource  type  you  want  to  un-share:
Submit  1  for  Files/Directories
Submit  2  for  Computational  Partition
> 1
Enter  the  resource  name  you  want  to  un-share:  /scratch/alex
Enter  the  user  names  to  un-share  with (space separated): cathy
Un-Sharing  /scratch/alex  Allowed:  From  alex  to  cathy
Collaboration  '{'bailey', 'cathy', 'alex'}'  removed  access  to  resource  '/scratch/alex'.
Collaboration  '{'bailey', 'alex'}'  granted  access  to  resource  '/scratch/alex'.
Project  '/etc/project/Project1.json'  created/updated  successfully.

# remove

sysadmin@linux0:~$  sudo  clears  remove
Enter  the  project  name:  Project1
Enter  the  user  names  to  remove (space separated): bailey
bailey(uid=10002) successfully removed from Project1
Collaboration  '{'alex', 'bailey'}'  removed  access  to  resource  '/scratch/alex'.
Project  '/etc/project/Project1.json'  created/updated  successfully.

# end

sysadmin@linux0:~$sudo  clears  end
Enter  the  project  name:  Project1
cathy(uid=10003) successfully removed from Project1
alex(uid=10001) successfully removed from Project1
Project  '/etc/project/Project1.json'  created/updated  successfully.
Project  Project1  ended  successfully!

```

## 📌 Citation

If you use **CLEARS** in your research, please cite:

```
@inproceedings{nath2025towards,
  title={{“Towards Collaboration-Aware Resource Sharing in Research Computing Infrastructures}},
  author={Nath, Souradip and Soneji, Ananta and Baek, Jaejong and Rubio-Medrano, Carlos and Ahn, Gail-Joon},
  booktitle={To Appear in 2025 11th IEEE International Conference on Collaboration and Internet Computing},
  year={2025},
  organization={IEEE}
}
```
