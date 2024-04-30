from classes.resource import Resource, Resources


def create_resource(resource_id: str, owner: str):
    resource = Resource(rid=resource_id, owner=owner)
    print(f"Resource {resource.get_rid()} (o: {resource.get_owner()}) Added!")
    add_resource(resource)


def get_resource(resource_id: str) -> Resource:
    if resource_id in Resources.resources.keys():
        return Resources.resources[resource_id]


def add_resource(resource: Resource):
    if resource.get_rid() in Resources.resources.keys():
        print("Resource already exists!")
        return
    else:
        Resources.resources[resource.get_rid()] = resource
        print(f"Resource {resource.get_owner()} Added!")


def remove_resource(resource_id: str):
    if resource_id not in Resources.resources.keys():
        print("No such resource exists!")
        return
    else:
        Resources.resources.pop(resource_id)
