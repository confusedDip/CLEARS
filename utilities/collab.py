from classes.collab import Network, Networks
from utilities.user import get_user, add_project, remove_project
from utilities.resource import get_resource


def start_project(user_ids: set[str], project_id: str):
    network = Network(user_ids=user_ids, project_id=project_id)
    # Add the network to the set of networks
    add_network(network)
    # Add the project to each user's project list
    add_project(user_ids=network.all_user_ids, project_id=network.project_id)


def end_project(project_id: str):
    network = get_network(project_id)
    # Remove the network from the set of networks
    remove_network(network)
    # Remove the project to each user's project list
    remove_project(user_ids=network.all_user_ids, project_id=network.project_id)
    # Delete the project
    del network


def add_network(network: Network):
    project_id = network.project_id

    if project_id not in Networks.networks.keys():
        Networks.networks[project_id] = network
        print(f"Collaboration Network for Project {project_id} added")
    else:
        print(f"Error: Collaboration Network for Project {project_id} already exists")


def remove_network(network: Network):
    project_id = network.project_id

    if project_id in Networks.networks.keys():
        del Networks.networks[project_id]
        print(f"Collaboration Network for Project {project_id} removed")
    else:
        print(f"Error: Collaboration Network for Project {project_id} does not exist")


def get_network(project_id: str) -> Network:
    if project_id in Networks.networks.keys():
        return Networks.networks[project_id]


def can_access(requester_id: str, resource_id: str) -> bool:
    print(f"Requester: {requester_id}, Requested Resource: {resource_id}")

    # Obtain the resource from the requested resource_id
    resource = get_resource(resource_id)
    # Obtain the owner uid
    owner_id = resource.get_owner()

    # Always allow the owner to access
    if requester_id == owner_id:
        return True

    # Obtain the mutual projects of the owner and the requestor
    owner_projects = get_user(owner_id).get_projects()
    requester_projects = get_user(requester_id).get_projects()
    mutual_projects = owner_projects.intersection(requester_projects)

    # If they do not work on any common project, deny!
    if len(mutual_projects) == 0:
        return False

    # Explore the collaboration network for each project to make a decision
    for project in mutual_projects:
        network = get_network(project)
        print(f"Checking the Collaboration Network for Project {project}")
        if network.can_access(requester_id, resource_id):
            return True
        else:
            print("False!")

    return False
