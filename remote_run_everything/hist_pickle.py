import os
import pickle


class Hist:
    def __init__(self, pick_dir):
        self.pick_dir = pick_dir  # self.c.local_root
        self.hist_pickle = os.path.join(pick_dir, "up_hist.pickle").replace("\\", "/")

    def get_upload_records(self):
        if os.path.exists(self.hist_pickle):
            with open(self.hist_pickle, 'rb') as file:
                try:
                    data = pickle.load(file)
                    return data
                except EOFError:
                    return None

    def save_upload_records(self, data):
        with open(self.hist_pickle, 'wb') as file:
            pickle.dump(data, file)

    def upload_record_or_not(self, host, file_path):
        # do not up myself
        if "up_hist.pickle" in file_path:
            return False
        already = self.get_upload_records()
        new_rev = os.path.getmtime(file_path)
        if already is not None:
            old_rev = already.get((host, file_path), None)
            if new_rev != old_rev:
                already[(host, file_path)] = new_rev
                self.save_upload_records(already)
                return True
            else:
                return False
        else:
            dic = {}
            dic[(host, file_path)] = new_rev
            self.save_upload_records(dic)
            return True

    def download_record_or_not(self, host, rpath, rmtime):
        # 本地文件,记录远程rmtime
        if "up_hist.pickle" in rpath:
            return False

        already = self.get_upload_records()
        new_rev = rmtime
        if already is not None:
            old_rev = already.get((host, rpath), None)
            # 远程发生了改变
            if new_rev != old_rev:
                already[(host, rpath)] = new_rev
                self.save_upload_records(already)
                return True
            else:
                return False
        else:
            dic = {}
            dic[(host, rpath)] = new_rev
            self.save_upload_records(dic)
            return True
