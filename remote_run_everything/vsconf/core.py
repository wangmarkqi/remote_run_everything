import os, shutil
from remote_run_everything.vsconf.conf_txt import *


class VsConf:
    def wf(self, path, s):
        base = os.path.dirname(path)
        if not os.path.exists(base):
            os.makedirs(base, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(s.encode())

    def vs_rust(self):
        self.wf(f"./.vscode/tasks.json", tasks_rs())
        self.wf(f"./.vscode/launch.json", launch_rs())

    def git_ignore(self):
        self.wf(f"./.gitignore", git())
