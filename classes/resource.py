from classes.user import User

class Resource:

    def __init__(self, rid, owner:User):
        self.rid = rid
        self.owner = owner
        print(f"Resource {self.rid} (o: {self.owner.getUID()}) Added!")

    def getRID(self):
        return self.rid
    
    def getOwner(self):
        return self.owner
