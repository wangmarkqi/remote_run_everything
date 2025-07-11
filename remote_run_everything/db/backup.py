from bson import BSON, decode_all
import pymongo
import os, sys


class BackUp:
    def __init__(self,  root):
        self.root = root
        os.makedirs(self.root, exist_ok=True)

    def mongo_dump(self,cli,dbs):
        for d in dbs:
            db = cli[d]
            dir = os.path.join(self.root, d)
            os.makedirs(dir, exist_ok=True)
            cols = db.list_collection_names()
            for col in cols:
                sr = db[col]
                # Dump.
                with open(f'{dir}/{col}.bson', 'wb+') as f:
                    for doc in sr.find():
                        f.write(BSON.encode(doc))

    def mongo_restore(self,cli,dbs):
        for d in dbs:
            db = cli[d]
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


