"""Cement methods and classes to handle cli option/arg parsing."""

import os
import sys
import re
import optparse

from cement.core.configuration import namespaces
from cement.core.log import get_logger
            
log = get_logger(__name__)            
        

def init_parser(banner=None):
    """
    Create an OptionParser object and returns its parser member.
    
    Keyword arguments:
    
        banner
            Optional version banner to display for --version
    
    Returns: OptionParser object.
    
    """
    fmt = optparse.IndentedHelpFormatter(
            indent_increment=4, max_help_position=32, width=77, short_first=1
            )
    parser = optparse.OptionParser(formatter=fmt, version=banner)
    return parser
    
def parse_options(namespace='root', ignore_conflicts=False): 
    """
    The actual method that parses the command line options and args.  Also
    handles all the magic that happens when you pass --help to your app.  It
    also handles merging root options into plugins, if the plugins config
    is set to do so (merge_root_options)
    
    Required Arguments:
    
        namespace
            The namespace to parse options for (defaullt: 'root')
    
    Returns: tuple (options, args)
    
    """

    # FIX ME: This method is very messy/confusing.
    
    log.debug("parsing command line opts/args for '%s' namespace" % namespace)
    if namespace != 'root':
        if namespaces[namespace].config.has_key('merge_root_options') and \
           namespaces[namespace].config['merge_root_options']:
            for opt in namespaces['root'].options._get_all_options(): 
                if opt.get_opt_string() == '--help':
                    pass
                elif opt.get_opt_string() == '--version':
                    pass
                else:
                    try:
                        namespaces[namespace].options.add_option(opt)
                    except optparse.OptionConflictError, error:
                        if not ignore_conflicts:
                            raise optparse.OptionConflictError, error
    commands_list = []
    if namespaces[namespace].commands:
        for cmd in namespaces[namespace].commands:    
            cmd_with_dashes = re.sub('_', '-', cmd)
            cmd_dict = namespaces[namespace].commands[cmd]
            if cmd_dict['is_hidden']:
                pass
            else:
                commands_list.append((cmd_with_dashes, cmd_dict['desc'] or ""))
    
    cmd_txt = ""
    if commands_list:
        cmd_txt = "  %%-%ds %%s" % (max((len(c[0]) for c in commands_list))+2)
        cmd_txt = "\n".join(cmd_txt % c for c in commands_list)
    
    # Do the same thing, but with namespaces (if applicable to each namespace)
    nam_txt = ''
    line = '    '
    namespaces_list = []
    script = os.path.basename(sys.argv[0])
    if namespace == 'root':
        for nam in namespaces: 
            nam_with_dashes = re.sub('_', '-', nam)
            if nam != 'root' and namespaces[nam].commands:
                if namespaces[nam].is_hidden:
                    pass
                else:
                    # dirty, but have to account for namespaces with only 
                    # hidden commands... which we don't want to show
                    show_namespace = False
                    for cmd in namespaces[nam].commands:
                        if not namespaces[nam].commands[cmd]['is_hidden']:
                            show_namespace = True
                            break

                    if show_namespace:
                        namespaces_list.append((nam_with_dashes, namespaces[nam].description or ""))
                        if line == '    ':
                            line += '%s' % nam_with_dashes
                        elif len(line) + len(nam_with_dashes) < 75:
                            line += ', %s' % nam_with_dashes
                        else:
                            nam_txt += "%s \n" % line
                            line = '    %s' % nam_with_dashes
        
        if namespaces_list:
            nam_txt = "  %%-%ds %%s" % (max((len(n[0]) for n in namespaces_list))+2)
            nam_txt = "\n".join(nam_txt % n for n in namespaces_list)
        
        if not nam_txt:
            namespaces[namespace].options.usage = """  %s <COMMAND> [ARGS] --(OPTIONS)

Commands:
%s
Help?  try '[COMMAND] --help' OR '[NAMESPACE] --help'""" % \
            (script, cmd_txt)

        else:
            namespaces[namespace].options.usage = """  %s <COMMAND> [ARGS] --(OPTIONS)

Commands:
%s

Namespaces (Nested SubCommands):
%s

Help?  try '[COMMAND] --help' OR '[NAMESPACE] --help'""" % \
        (script, cmd_txt, nam_txt)
                         
    else: # namespace not root
        namespaces[namespace].options.usage = """  %s %s <SUBCOMMAND> [ARGS] --(OPTIONS)

%s

Sub-Commands:
%s""" % \
        (script, re.sub('_', '-', namespace), namespaces[namespace].description, cmd_txt)
    
    args = filter(lambda x: not x.startswith('-'), sys.argv)
    if len(args) > 2 and namespaces[namespace].commands.has_key(args[2]):
        # Show a command help-text
        cmd_name = args[2]
        cmd = namespaces[namespace].commands[cmd_name]
        namespaces[namespace].options.usage = """   %s %s %s [ARGS] --(OPTIONS)

%s
""" % (script, re.sub('_', '-', namespace), cmd_name, cmd.get("desc", "") )

    (opts, args) = namespaces[namespace].options.parse_args()
    
    return (opts, args)

