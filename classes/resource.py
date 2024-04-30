from classes.user import User


class Resource:

    def __init__(self, rid: str, owner: User):
        self.__rid = rid
        self.__owner = owner
        print(f"Resource {self.__rid} (o: {self.__owner.get_uid()}) Added!")
        add_resource(self)

    def get_rid(self) -> str:
        return self.__rid

    def get_owner(self):
        return self.__owner


def add_resource(resource: Resource):

    if resource.get_rid() in Resources.resources.keys():
        print("Resource already exists!")
        return
    else:
        Resources.resources[resource.get_rid()] = resource
        print(f"Resource {resource.get_owner()} Added!")


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

