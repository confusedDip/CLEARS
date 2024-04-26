from classes.user import User


class Resource:

    def __init__(self, rid: str, owner: User):
        self.rid = rid
        self.owner = owner
        print(f"Resource {self.rid} (o: {self.owner.get_uid()}) Added!")
        add_resource(self)

    def get_rid(self) -> str:
        return self.rid

    def get_owner(self):
        return self.owner


def add_resource(resource: Resource):

    if resource.rid in Resources.resources.keys():
        print("Resource already exists!")
        return
    else:
        Resources.resources[resource.rid] = resource
        print(f"Resource {resource.rid} Added!")


def get_resource(resource_id: str) -> Resource:

    if resource_id in Resources.resources.keys():
        return Resources.resources[resource_id]


def remove_resource(resource_id: str):

    if resource_id not in Resources.resources.keys():
        print("No such resource exists!")
        return
    else:
        Resources.resources.pop(resource_id)


class Resources:

    resources: [str, Resource] = {}

