# CLEARS: Collaboration-aware Authorization of Resource Sharing

In this work, we propose and implement a novel Collaboration-aware Access Control framework, which integrates project-specific collaborations and selective resource sharing to aid administrators in uniformly managing shared privileges within collaborative contexts, streamlining access decision-making while upholding the principle of least privilege to prevent unauthorized access in Research Computing environments.

## Environmental Setup

The current implementation is tested in a simulated virtual environment emulating an RC setup. This environment consists of three virtual machines: `linux0`, `linux1`, and `linux3`. Each VM runs Ubuntu 22.04.03 LTS Server and is connected through a bridged network using an Intel PRO/1000 MT Desktop adapter.

For detailed instructions on setting up the environment, refer to the `guides` folder.

## Installation

Follow these steps to install and set up the project:

#### 1. Clone the Repository
```bash
   git clone <repository url>
   cd /path/to/the/repository
```

#### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

#### 3. Set Up the Deployment Directory
Create a directory for the application:

```bash
sudo mkdir /usr/bin/authz
```

#### 4. Copy the Repository Contents
Copy all files from the repository to the newly created directory:

```bash
sudo cp * -r /usr/bin/authz
```

#### 5. Set File Permissions
Update permissions for specific utilities:

```bash
sudo chmod +s /usr/bin/authz/utilities/wrapper_network_dump
sudo chmod +s /usr/bin/authz/utilities/wrapper_supdate
```

#### 6. Create a Symbolic Link
Link the entry point of the codebase (main.py) to an executable named `clears` (or whatever name you prefer):

```bash
sudo ln -s /usr/bin/authz/main.py /usr/bin/clears
sudo chmod +x /usr/bin/clears
```

#### 7. Run the Application
Start the application to verify the setup:

```bash
clears help
```


## Usage
The clears command-line tool allows administrators to efficiently manage shared privileges within collaborative projects. Below are the available commands:

```bash
clears(1)

NAME
    clears - efficiently manage shared privileges

SYNOPSIS
    clears [COMMAND..]

COMMANDS
    start   Start a new project. (requires administrative privileges to perform)
    
    add     Add collaborators to an existing project. (requires administrative privileges to perform)
    
    share   Share privileges with a collaborator to access resources within a project.
    
    unshare Retract previously shared privileges from a collaborator within a project.
    
    remove  Remove collaborators from an existing project. (requires administrative privileges to perform)
    
    end     End an existing project. (requires administrative privileges to perform)
    
    help    Launch the help menu.
```
