# Collaboration-aware Authorization of Resource Sharing

## Environmental Setup

The current implementation of our proposed access control model is tested in a simulated virtual environment
emulating an actual Research Computing (RC) environment. The environment consists of three virtual machines - `linux0`,
`linux1` and `linux3` - each running Ubuntu 22.04.03 LTS Server and connected through a bridged network using an Intel
PRO/1000 MT Desktop adapter.

Detailed walkthrough for the environmental setup can be found in the `guides` folder.

## Installation

- Clone the Repository
- Install the dependencies from `requirements.txt`
- Create an empty repository at `/usr/bin/authz`
- Copy the entire contents of the repository to `/usr/bin/authz`
- Update the default permissions to the files accordingly
- Create a symbolic link to the entry point of the codebase `main.py` named `authzmodel` and make it executable
- Run `authzmodel`

```bash!
$ git clone <repository url>
$ cd /path/to/the/repository
$ pip3 install -r requirements.txt
$ sudo mkdir /usr/bin/authz
$ sudo cp * -r /usr/bin/authz
$ sudo chmod +s /usr/bin/authz/utilities/wrapper_network_dump
$ sudo chmod +s /usr/bin/authz/utilities/wrapper_supdate
$ sudo ln -s /usr/bin/authz/main.py /usr/bin/authzmodel
$ sudo chmod +x /usr/bin/authzmodel
$ authzmodel help
```

## Usage

```commandline
authzmodel(1)

NAME
	authzmodel - efficiently manage shared privileges

SYNOPSIS
	authzmodel [COMMAND..]

COMMANDS
	start	Start a new project. (requires administrative privileges to perform)

	add	Add collaborators to an existing project. (requires administrative privileges to perform)

	share	Share privileges with a collaborator to access resources within a project.

	unshare	Retract previously shared privileges from a collaborator within a project.

	remove	Remove collaborators from an existing project. (requires administrative privileges to perform)

	end	End an existing project. (requires administrative privileges to perform)

	help	Launch the help menu.
```
