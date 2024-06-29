from __future__ import annotations;
from typing import *;
import inspect as ins;
import sys, os, pathlib;
__actual_file__   = pathlib.Path(ins.getabsfile(ins.currentframe())).resolve();
__actual_dir__    = os.path.dirname(__actual_file__);
if __name__ == '__main__' and not __package__:
	__actual_parent__ = os.path.dirname(__actual_dir__ );
	sys.path.insert(0, __actual_parent__);
	__package__ = os.path.split(__actual_dir__)[1];
pass

import json, subprocess;

class Startup(TypedDict):
	testing: bool;
	pid: None | int;
pass
startup_filename = __actual_dir__ + "/startup.json";
with open(startup_filename) as f: startup: Startup = json.load(f);
startup["pid"] = None;
with open(startup_filename, "w") as f: json.dump(startup, f);

sys.exit(subprocess.run([sys.executable, __actual_dir__ + "/StickyThrough.pyw"]));
