
import os
import sys

import distutils.core

if len(sys.argv) < 1:
    raise SystemExit("Need at least the package to upload")

#
# run_setup starts here. It was copied because we needn't pass locals dict to
# execfile
distutils.core._setup_stop_after = 'init'
script_name = 'setup.py'

save_argv = sys.argv
g = {'__file__': script_name}
l = {}
try:
    try:
        sys.argv = [script_name]
        execfile(script_name,g)
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

dist.commands = ['upload']
dist.dist_files = [('command', 'version', os.path.abspath(sys.argv[1]))]
dist.command_options = {
    'upload': {'repository': ('command line', 'spynepi')},
}

dist.run_commands()
