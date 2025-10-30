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
    def vim_rc(self):
        self.wf("~/.ideavimrc",idea_vim())
        self.wf("~/.vimrc",idea_vim())
    def conda_rc(self):
        self.wf("~/.condarc",conda_rc())
        if os.name=="nt":
            self.wf("~/pip/pip.ini",pip_rc())
        else:
            self.wf("~/.pip/pip.conf",pip_rc())


