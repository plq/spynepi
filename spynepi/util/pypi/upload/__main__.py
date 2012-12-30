
import os
import sys

import distutils.core

print os.getcwd()

#
# run_setup starts here
distutils.core._setup_stop_after = 'init'
script_name = 'setup.py'

save_argv = sys.argv
g = {'__file__': script_name}
l = {}
try:
    try:
        sys.argv = [script_name]
        execfile(script_name)# in g, l
    finally:
        sys.argv = save_argv
        _setup_stop_after = None
except SystemExit:
    pass
except:
    raise

if distutils.core._setup_distribution is None:
    raise RuntimeError, \
          ("'distutils.core.setup()' was never called -- "
           "perhaps '%s' is not a Distutils setup script?") % \
          script_name

dist = distutils.core._setup_distribution
# run_setup ends here
#

print sys.argv
dist.commands = ['upload']
dist.dist_files = [('command', 'version', os.path.abspath(sys.argv[1]))]
dist.command_options = {
    'upload': {'repository': ('command line', 'spynepi')},
}

dist.run_commands()
