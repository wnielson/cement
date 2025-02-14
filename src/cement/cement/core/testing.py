"""Helper functions for testing applications built on Cement."""

import sys
import re

from cement.core.exc import CementRuntimeError
from cement.core.command import run_command

def simulate(args):
    """
    Simulate running a command at command line.  Requires args to have
    the exact args set to it as would be passed at command line.
    
    Required arguments:
    
        args
            The args to pass to sys.argv
            
    Usage:
    
    .. code-block:: python
    
        import sys
        from cement.core.testing import simulate
        
        args = ['helloworld', 'example', 'cmd1', '--test-option']
        res = simulate(args)
        
    """
    if not len(sys.argv) >= 1:
        raise CementRuntimeError, "args must be set properly."
        
    sys.argv = args
    try:
        cmd = re.sub('-', '_', sys.argv[1])
    except IndexError:
        cmd = 'default'
        
    (res_dict, output_txt) = run_command(cmd_name=cmd, ignore_conflicts=True)
    return (res_dict, output_txt)
