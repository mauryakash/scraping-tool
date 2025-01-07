import json
import os

class Storage:
    def __init__(self, filename="db.json"):
        self.filename = filename

    def save(self, product):
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump([], f)

        with open(self.filename, "r") as f:
            data = json.load(f)

        data.append(product)

        with open(self.filename, "w") as f:
            json.dump(data, f, indent=4)
    
    def load(self):
        if not os.path.exists(self.filename):
            return []
        with open(self.filename, "r") as f:
            return json.load(f)