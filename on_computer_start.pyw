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

SHOULD_NOT_CLOSE_FILE = __actual_dir__ + "/should_not_close";
try: os.remove(SHOULD_NOT_CLOSE_FILE);
except: pass;

sys.exit(subprocess.run([sys.executable, __actual_dir__ + "/StickyThrough.pyw"]));
