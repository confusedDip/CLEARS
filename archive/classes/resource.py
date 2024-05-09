class Resource:

    def __init__(self, rid: str, owner: str):
        self.__rid = rid
        self.__owner = owner

    def get_rid(self) -> str:
        return self.__rid

    def get_owner(self):
        return self.__owner


class Resources:
    resources: [str, Resource] = {}
