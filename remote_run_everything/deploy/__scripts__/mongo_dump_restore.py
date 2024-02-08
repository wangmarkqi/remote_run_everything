from bson import BSON, decode_all
import pymongo
import os, sys
class MongoTool:
    def __init__(self, url,dbs):
        self.cli = pymongo.MongoClient(url)
        # self.dbs =["mpy","ruihe","iron"]
        self.dbs = dbs
        self.root = self.get_root_dir()
    
    def get_root_dir(self):
        cur = os.path.dirname(__file__)
        upper = os.path.dirname(cur)
        root = os.path.join(upper, 'mongo_backup')
        os.makedirs(root, exist_ok=True)
        return root
    
    def dump(self):
        for d in self.dbs:
            db = self.cli[d]
            dir = os.path.join(self.root, d)
            os.makedirs(dir, exist_ok=True)
            cols = db.list_collection_names()
            for col in cols:
                sr = db[col]
                # Dump.
                with open(f'{dir}/{col}.bson', 'wb+') as f:
                    for doc in sr.find():
                        f.write(BSON.encode(doc))
    
    def restore(self):
        for d in self.dbs:
            db = self.cli[d]
            dir = os.path.join(self.root, d)
            files = os.listdir(dir)
            cols = [i.split('.')[0] for i in files]
            print(cols)
            for name in cols:
                file = f"{dir}/{name}.bson"
                col = db[name]
                with open(file, 'rb') as f:
                    data = decode_all(f.read())
                    col.insert_many(data)
if __name__ == '__main__':
    # mongodb://localhost:27017
    which =sys.argv[1]
    url=sys.argv[2]
    dbs=sys.argv[3:]
    m = MongoTool(url,dbs)
    if which=="dump":
        m.dump()
    if which=="restore":
        m.restore()
